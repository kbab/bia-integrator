import os
import json
import logging
import urllib.parse

import click
from jinja2 import Environment, FileSystemLoader, select_autoescape

from bia_integrator_core.study import get_study
from bia_integrator_core.interface import get_image, to_uuid
from scripts.extract_ome_metadata import sanitise_image_metadata

from utils import format_for_html, DOWNLOADABLE_REPRESENTATIONS

logger = logging.getLogger(os.path.basename(__file__))


LICENSE_URI_LOOKUP = {
    "CC0": "https://creativecommons.org/publicdomain/zero/1.0/",
    "CC BY 4.0": "https://creativecommons.org/licenses/by/4.0/"
}

env = Environment(
    loader = FileSystemLoader("templates"),
    autoescape=select_autoescape()
)

template = env.get_template("image-landing.html.j2")

def sig_format(n):
    inte = int(n)
    n -= inte
    return str(inte + float("{0:.2g}".format(n)))

def sort_dict(d):
    """Return dictionary with keys sorted alphabetically"""
    return {key: d[key] for key in sorted(d)}

def generate_neuroglancer_link(uri: str):
    """Given the URI of a Zarr image, return a Neuroglancer URI that will open that image as the default
    image layer."""

    viewer_state_obj = {
      "layers": [
        {
          "type": "image",
          "source": "zarr://{zarr_uri}".format(zarr_uri=uri),
          "tab": "source",
          "name": "Image"
        }
      ],
      "layout": "4panel"
    }

    viewer_json_str = json.dumps(viewer_state_obj)
    viewer_state_no_spaces = viewer_json_str.replace(" ", "")
    
    neuroglancer_uri = "https://neuroglancer-demo.appspot.com/#!" + urllib.parse.quote_plus(viewer_state_no_spaces, safe=":{}/,[]")
    
    return neuroglancer_uri


def generate_image_page_html(accession_id: str, image_uuid):

    bia_study = get_study(accession_id)
    bia_image = get_image(image_uuid)
    author_names = ', '.join([ 
        author.name
        for author in bia_study.authors
    ])

    reps_by_type = {
        representation.type: representation
        for representation in bia_image.representations
    }

    image_alias = bia_image.alias.name if bia_image.alias else None

    # Format physical dimensions to X unit x Y unit x Z unit format before passing on to the template
    psize = None
    px = py = pz = None
    if bia_image.attributes.get('PhysicalSizeX'):
        px = sig_format(float(bia_image.attributes['PhysicalSizeX']))
        py = sig_format(float(bia_image.attributes['PhysicalSizeY']))  
        psize = '{} {} x {} {}'.format(px,bia_image.attributes[u'PhysicalSizeXUnit'],py,bia_image.attributes[u'PhysicalSizeYUnit'])
        if bia_image.attributes.get('PhysicalSizeZ'):
            pz = sig_format(float(bia_image.attributes['PhysicalSizeZ']))
            psize += ' x {} {}'.format(pz,str(bia_image.attributes['PhysicalSizeZUnit']))
    
    # Convert image dimensions to X x Y x Z format before passing on to the template
    dims = None
    dx = dy = dz = None
    if bia_image.dimensions :
        dl = bia_image.dimensions.split(',')
        if dl[0].startswith('('):
            dl[0] = dl[0].split('(')[1]
            dx = dl[-1].split(')')[0]
            dy = dl[-2]
            dims = dx + ' x ' + dy 
            if dl[-3].strip() != '1':
                dz = dl[-3]
                dims += ' x ' + dz
        else:
            dims = bia_image.dimensions
    elif bia_image.attributes.get('SizeX'):
        dx = bia_image.attributes['SizeX']
        dy = bia_image.attributes['SizeY']
        dims = str(dx) + ' x ' + str(dy)
        if bia_image.attributes['SizeZ'].strip() != '1':
            dz = bia_image.attributes['SizeZ']
            dims += ' x ' + str(dz)

    pdims = None        
    if dx and px:
        pdims = "{0:.1f}".format(float(dx)*float(px)) + bia_image.attributes[u'PhysicalSizeXUnit'] + ' x ' \
            + "{0:.1f}".format(float(dy)*float(py)) + bia_image.attributes[u'PhysicalSizeYUnit']
        if dz and pz:
            pdims += ' x ' + "{0:.1f}".format(float(dz)*float(pz)) + bia_image.attributes[u'PhysicalSizeZUnit']


    # If an attribute is in form of json format to display indented in html
    bia_image.attributes = sort_dict(sanitise_image_metadata(bia_image.attributes))
    for key, attribute in bia_image.attributes.items():
        try:
            if attribute.find("{") >= 0:
                bia_image.attributes[key] = format_for_html(attribute)
        except Exception:
            # Skip if any errors
            continue

    download_uri = None
    for rep_type in DOWNLOADABLE_REPRESENTATIONS:
        if rep_type in reps_by_type:
            download_uri = urllib.parse.quote(reps_by_type[rep_type].uri[0], safe=":/")
            break
    
    try:
        download_size = bia_image.attributes["download_size"]
    except KeyError:
        download_size = "?MiB"

    zarr_uri = reps_by_type["ome_ngff"].uri[0]


    #TODO: Discuss with LA/MH
    try:
        license_uri = LICENSE_URI_LOOKUP.get(bia_study.license, "Unknown")
    except AttributeError:
        license_uri = "Unknown"


    rendered = template.render(
        study=bia_study,
        license_uri=license_uri,
        image=bia_image,
        image_alias=image_alias,
        zarr_uri=zarr_uri,
        psize=psize,
        pdims=pdims,
        dimensions=dims,
        authors=author_names,
        download_uri=download_uri,
        download_size=download_size
    )

    return rendered


@click.command()
@click.argument("accession_id")
@click.argument("image_uuid")
def main(accession_id, image_uuid):

    logging.basicConfig(level=logging.INFO)

    rendered = generate_image_page_html(accession_id, image_uuid)

    print(rendered)




if __name__ == "__main__":
    main()
