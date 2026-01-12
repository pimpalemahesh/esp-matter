"""
Script to generate the delegate implementation section of app_guide.rst
This ensures the cluster list is always sorted and reduces code repetition.
"""
import os
from delegate_clusters import CLUSTERS

def generate_cluster_display_names(clusters: list[dict]) -> str:
    """Generate the bullet list of clusters with delegates"""
    output = []
    for cluster in clusters:
        output.append(f"    - {cluster['display_name']}.")
    return "\n".join(output)


def generate_cluster_sections(clusters: list[dict]) -> str:
    """Generate the individual cluster sections with CSV tables"""
    output = []

    for idx, cluster in enumerate(clusters, start=1):
        section_num = f"1.{idx}"
        display_name = cluster["display_name"]

        output.append(f"{section_num} {display_name}")
        output.append("~" * len(f"{section_num} {display_name}"))
        output.append("")

        if "note" in cluster:
            output.append(cluster["note"])
            output.append("")

        output.append(".. csv-table::")
        output.append('  :header: "Delegate Class", "Reference Implementation"')
        output.append("")

        delegate_ref = f"`{cluster['delegate_link_name']}`_"

        if "multiple_impl_link_urls" in cluster:
            for idx, (impl_name, impl_url) in enumerate(cluster["multiple_impl_link_urls"]):
                if idx == 0:
                    output.append(f"  {delegate_ref}, `{impl_name}`_")
                else:
                    impl_ref = f"`{impl_name}`_" if impl_url else f"`{impl_name}`"
                    output.append(f"{' ' * (len(delegate_ref) + 2)}, {impl_ref}")
        elif cluster["delegate_impl_link_name"]:
            impl_ref = f"`{cluster['delegate_impl_link_name']}`_"
            output.append(f"  {delegate_ref}, {impl_ref}")
        else:
            output.append(f"  {delegate_ref}, None")

        output.append("")

    return "\n".join(output)


def generate_reference_links(clusters: list[dict]) -> str:
    """Generate the reference link definitions"""
    output = []

    links = {}

    for cluster in clusters:
        links[cluster["delegate_link_name"]] = cluster["delegate_link_url"]

        if "multiple_impl_link_urls" in cluster:
            for impl_name, impl_url in cluster["multiple_impl_link_urls"]:
                if impl_url:
                    links[impl_name] = impl_url
        elif cluster["delegate_impl_link_name"] and cluster["delegate_impl_link_url"]:
            links[cluster["delegate_impl_link_name"]] = cluster[
                "delegate_impl_link_url"
            ]

    for link_name in links.keys():
        output.append(f".. _`{link_name}`: {links[link_name]}")

    return "\n".join(output)

def generate_delegate_section_document(clusters: list[dict]) -> str:
    """Generate the complete delegate implementation section"""
    header = """Application User Guide
======================

1. Delegate Implementation
--------------------------

As per the implementation in the connectedhomeip repository, some of the clusters
require an application defined delegate to consume specific data and actions.
In order to provide this flexibity to the application, esp-matter facilitates delegate
initilization callbacks in the cluster create API. It is expected that application
will define it's data and actions in the form of delegate-impl class and set the
delegate while creating cluster/device type.

List of clusters with delegate:
"""

    intro = """
Below is the list of clusters with delegate and their reference implementation header files:

"""
    note = """.. note::
    Make sure that after implementing delegate class, you set the delegate class pointer at the time of creating cluster.

   ::

      robotic_vacuum_cleaner::config_t rvc_config;
      rvc_config.rvc_run_mode.delegate = object_of_delegate_class;
      endpoint_t *endpoint = robotic_vacuum_cleaner::create(node, & rvc_config, ENDPOINT_FLAG_NONE);
"""

    output = [header]
    output.append(generate_cluster_display_names(clusters))
    output.append(intro)
    output.append(generate_cluster_sections(clusters))
    output.append(note)
    output.append(generate_reference_links(clusters))
    output.append("")

    return "\n".join(output)

if __name__ == "__main__":

    sorted_clusters = sorted(CLUSTERS, key=lambda x: x["display_name"])
    content = generate_delegate_section_document(sorted_clusters)
    curr_file_path = os.path.dirname(os.path.abspath(__file__))
    output_file = os.path.join(curr_file_path, "..", "..", "docs", "en", "app_guide.rst")
    with open(output_file, "w") as f:
        f.write(content)
    print(f"Generated {output_file}")
