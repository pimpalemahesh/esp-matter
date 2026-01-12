import sys
from delegate_clusters import CLUSTERS

"""
Script to generate the delegate implementation section of app_guide.rst
This ensures the cluster list is always sorted and reduces code repetition.
"""

def generate_cluster_list():
    """Generate the bullet list of clusters with delegates"""
    output = []
    for cluster in sorted(CLUSTERS, key=lambda x: x["display_name"]):
        output.append(f"    - {cluster['display_name']}.")
    return "\n".join(output)


def generate_cluster_sections():
    """Generate the individual cluster sections with CSV tables"""
    output = []
    sorted_clusters = sorted(CLUSTERS, key=lambda x: x["display_name"])

    for idx, cluster in enumerate(sorted_clusters, start=1):
        section_num = f"1.{idx}"
        display_name = cluster["display_name"]

        # Create section header
        output.append(f"{section_num} {display_name}")
        output.append("~" * len(f"{section_num} {display_name}"))
        output.append("")

        # Add note if present
        if "note" in cluster:
            output.append(cluster["note"])
            output.append("")

        # Create CSV table
        output.append(".. csv-table::")
        output.append('  :header: "Delegate Class", "Reference Implementation"')
        output.append("")

        # Add delegate class reference
        delegate_ref = f"`{cluster['delegate_link_name']}`_"

        # Handle different implementation scenarios
        if "multiple_impl_link_urls" in cluster:
            # Multiple implementations
            impl_ref = f"`{cluster['multiple_impl_link_urls'][0][0]}`_"
            output.append(f"  {delegate_ref}, {impl_ref}")
            for impl_name, _ in cluster["multiple_impl_link_urls"][1:]:
                if impl_name:
                    impl_ref = f"`{impl_name}`_" if _ else impl_name
                    output.append(f"              , {impl_ref}")
        elif cluster["delegate_impl_link_name"]:
            # Single implementation
            impl_ref = f"`{cluster['delegate_impl_link_name']}`_"
            output.append(f"  {delegate_ref}, {impl_ref}")
        else:
            # No implementation
            output.append(f"  {delegate_ref}, None")

        output.append("")

    return "\n".join(output)


def generate_reference_links():
    """Generate the reference link definitions"""
    output = []

    links = {}

    for cluster in CLUSTERS:
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


def generate_note_section():
    """Generate the note section with example code"""
    return """.. note::
    Make sure that after implementing delegate class, you set the delegate class pointer at the time of creating cluster.

   ::

      robotic_vacuum_cleaner::config_t rvc_config;
      rvc_config.rvc_run_mode.delegate = object_of_delegate_class;
      endpoint_t *endpoint = robotic_vacuum_cleaner::create(node, & rvc_config, ENDPOINT_FLAG_NONE);
"""


def generate_full_document():
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

    output = [header]
    output.append(generate_cluster_list())
    output.append(intro)
    output.append(generate_cluster_sections())
    output.append(generate_note_section())
    output.append(generate_reference_links())

    return "\n".join(output)


if __name__ == "__main__":
    content = generate_full_document()

    output_file = "app_guide.rst"
    with open(output_file, "w") as f:
        f.write(content)
    print(f"Generated {output_file}")
