<!-- toc-name: Repository Root; -->

# Repository Markdown Table-of-Contents Generator

Used to automatically generate a table of contents of all Markdown files in a repository. 

## Table of Contents
<!-- TOC START -->
<!-- TOC END -->


## Adding Documentation Files

Any Markdown (`.md`) files added to this repository will automatically be indexed and added to the above table of contents.

Table of Contents is automatically removed and regenerated between the first set of table of content tags, as indicated by `<!-- TOC START -->` and `<!-- TOC END -->`. This process happens automatically via the `Update Table of Contents` action specified by the [update-toc.yml](.github/workflows/update-toc.yml) in [.github/workflows](.github/workflows). 

Table update functionality is handled via the [update-readme-toc.py](scripts/toc-generator.py) Python script in [scripts/](scripts/)

If a directory contains a `README.md` file, the directory will appear in the table of contents as a link pointing to the `README.md` file.

If you do not want a directory containing Markdown files to be indexed, simply add a file named `.toc-ignore` to it.

You can control how entries appear in the table of contents using special tags near the start of your file. These tags must appear at the start of the file.

### Table of Contents Control Tags

| Tag | Example | Description |
| --- | ------- | ----------- |
| toc-name | `<!-- toc-name: Custom Name; -->` | Sets a custom name for this file's entry in the table of contents. If this file is a README.md, the custom name will be applied to the directory listing instead. |
| toc-order | `<!-- toc-order: 1 -->` | Sets the order group of the table of contents item. This dictates the order in which entries appear within the context of their parent directory. Using `last` instead of an integer will result in the entry using the highest possible order group. Any entry that does not explicitly set this will be assigned to the order group immediately before the last one. |
| toc-ignore | `<!-- toc-ignore; -->` | Excludes this file from the table of contents. |

---

[Back to top](#documentation)
