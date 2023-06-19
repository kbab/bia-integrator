from typing import Dict, List, Optional

import zarr
import numpy as np
import dask.array as da
from PIL import Image
from pydantic import BaseModel
from microfilm.colorify import multichannel_to_rgb
from matplotlib.colors import LinearSegmentedColormap

from bia_integrator_core.interface import get_image
from bia_integrator_tools.utils import get_ome_ngff_rep_by_accession_and_image
from .omezarrmeta import ZMeta


DEFAULT_COLORS = [
    [1, 0, 0],
    [0, 1, 0],
    [0, 0, 1],
    [0, 1, 1],
    [1, 0, 1],
    [1, 1, 0]
]

DEFAULT_COLORMAPS = [
    LinearSegmentedColormap.from_list(f'n{n}', ([0, 0, 0], cmap_end))
    for n, cmap_end in enumerate(DEFAULT_COLORS)
]


class BIAProxyImage(object):

    def __init__(self, accession_id, image_id):
        self.bia_image = get_image(accession_id, image_id)
        self.ome_ngff_rep = get_ome_ngff_rep_by_accession_and_image(accession_id, image_id)
        self._init_darray()
        self.zgroup = zarr.open_group(self.ome_ngff_rep.uri)

        self.ngff_metadata = ZMeta.parse_obj(self.zgroup.attrs.asdict())
        
    def _init_darray(self):
        self.darray = dask_array_from_ome_ngff_rep(self.ome_ngff_rep)
        size_t, size_c, size_z, size_y, size_x = self.darray.shape
        
        self.size_t = size_t
        self.size_c = size_c
        self.size_z = size_z
        self.size_y = size_y
        self.size_x = size_x

    def get_dask_array_with_min_dimensions(self, dims):
        ydim, xdim = dims
        path_keys = [dataset.path for dataset in self.ngff_metadata.multiscales[0].datasets]

        for path_key in reversed(path_keys):
            zarr_array = self.zgroup[path_key]
            _, _, _, size_y, size_x = zarr_array.shape
            if (size_y >= ydim) and (size_x >= xdim):
                break
        
        return da.from_zarr(zarr_array)
    
    @property
    def all_sizes(self):
        path_keys = [dataset.path for dataset in self.ngff_metadata.multiscales[0].datasets]

        for path_key in path_keys:
            zarr_array = self.zgroup[path_key]
            yield zarr_array.shape





class ChannelRenderingSettings(BaseModel):
    """Rendering settings for a specific channel."""

    label: Optional[str]
    colormap_start: List[float] = [0., 0., 0.]
    colormap_end: List[float]
    window_start: Optional[int]
    window_end: Optional[int]


class BoundingBox2DRel(BaseModel):
    """Bounding box within a plane, described in relative coordniates such that
    1.0 is the full width/height of the plane image."""

    x: float
    y: float
    xsize: float
    ysize: float


class BoundingBox2D(BaseModel):
    """Bounding box within a plane, described in absolute coordinates."""

    x: int
    y: int
    xsize: int
    ysize: int


# FIXME - naming
class PlaneRegionSelection(BaseModel):
    """A 2D rectangular region."""

    t: int
    z: int
    c: int
    xmin: int
    xmax: int
    ymin: int
    ymax: int


class RenderingView(BaseModel):
    """A view of a BIAImage that should provide settings to produce a 2D image.
    
    Used for, e.g., generating thumbnails or example images."""

    t: int = 0
    z: int = 0
    region: Optional[PlaneRegionSelection]

    channel_rendering: Dict[int, ChannelRenderingSettings]


def scale_to_uint8(array):
    """Given an input array, convert to uint8, including scaling to fill the
    0-255 range. 
    
    Primarily used to convert general numpy arrays into an image rendering
    suitable dtype."""

    scaled = array.astype(np.float32)

    if scaled.max() - scaled.min() == 0:
        return np.zeros(array.shape, dtype=np.uint8)

    scaled = 255 * (scaled - scaled.min()) / (scaled.max() - scaled.min())

    return scaled.astype(np.uint8)


def apply_window(array, window_start, window_end):
    """Apply a windowing function to the given array, values above or below
    the window are clipped to the edges, and the range is scaled to the
    window range."""
    
    scaled = (array - window_start) / (window_end - window_start)
    clipped = np.clip(scaled, 0, 1)
    
    return clipped


def generate_channel_renderings(n_channels):
    """Generate a list channel renderings for a number of channels."""

    threemap_ends = [
        [1, 0, 0],
        [0, 1, 0],
        [0, 0, 1]
    ]

    channel_renderings = {
        n: ChannelRenderingSettings(colormap_end=colormap_end)
        for n, colormap_end in enumerate(threemap_ends)
    }

    return channel_renderings


def dask_array_from_ome_ngff_rep(ome_ngff_rep):
    """Get a dask array from an OME-NGFF image representation."""

    zgroup = zarr.open(ome_ngff_rep.uri)
    # FIXME - this should not be hard coded, it may break on spec-conformant images that are not generated by bioformats2raw
    path_key = '0'

    darray = da.from_zarr(zgroup[path_key])

    return darray


def select_region_from_dask_array(darray, region):
    """Select a single plane from a Dask array, and compute it."""

    return darray[region.t, region.c, region.z, region.ymin:region.ymax, region.xmin:region.xmax].compute()


def render_multiple_2D_arrays(arrays, colormaps):
    """Given a list of 2D arrays and a list of colormaps, apply each colormap
    merge into a single 2D RGB image."""

    imarray, _, _, _ = multichannel_to_rgb(arrays, colormaps)
    im = Image.fromarray(scale_to_uint8(imarray))
    
    return im


def best_efforts_render_image(accession_id, image_id, dims=(512, 512)):
    """In order to render a 2D plane we need to:
    
    1. Lazy-load the image as a Dask array.
    2. Select the plane (single t and z values) we'll use.
    3. Separate channels.
    4. Apply a color map to each channel array.
    5. Merge the channel arrays."""
    
    bia_proxy_im = BIAProxyImage(accession_id, image_id)

    t = bia_proxy_im.size_t // 2
    z = bia_proxy_im.size_z // 2
    
    region_per_channel = {
        c: PlaneRegionSelection(
            t=t,
            z=z,
            c=c,
            ymin=0,
            ymax=bia_proxy_im.size_y,
            xmin=0,
            xmax=bia_proxy_im.size_x
        )
        for c in range(bia_proxy_im.size_c)
    }

    darray = bia_proxy_im.get_dask_array_with_min_dimensions(dims)

    channel_arrays = {c: select_region_from_dask_array(darray, region) for c, region in region_per_channel.items()}

#     channel_arrays = {c: apply_window(array, 0, 150) for c, array in channel_arrays.items()}

    cmaps = DEFAULT_COLORMAPS[:bia_proxy_im.size_c]

    im = render_multiple_2D_arrays(channel_arrays.values(), cmaps)
    
    return im