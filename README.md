<!-- toc-name: Information; -->

# Markdown Table-of-Contents Generator

Used to automatically generate a table of contents in a target file from all Markdown files in a directory and its subdirectories. 

## Table of Contents
<!-- toc-start -->
- [Examples](README.md)
  - [README](Examples/README.md)
  - [Renamed Directory Entry Example](README.md)
    - [Renamed Directory Entry Example](Examples/Renamed%20Folder%20Example/README.md)
  - [Sub File Example](Examples/SubFileExample.md)
  - Ordered Group Example
    - [SomeFile (1)](Examples/Ordered%20Group%20Example/SomeFile%20%281%29.md)
    - [AnotherFile (2)](Examples/Ordered%20Group%20Example/AnotherFile%20%282%29.md)
    - [TheLastFile (3)](Examples/Ordered%20Group%20Example/TheLastFile%20%283%29.md)
  - Sub-Group Examples
    - [Plain-File](Examples/Sub-Group%20Examples/Plain-File.md)
<!-- toc-end -->


## Adding Documentation Files

Any Markdown (`.md`) files added to this repository will automatically be indexed and added to the above table of contents.

Table of Contents is automatically removed and regenerated between the first set of table of content tags, as indicated by `<!-- TOC START -->` and `<!-- TOC END -->`. This process happens automatically via the `Update Table of Contents` action specified by the [update-toc.yml](.github/workflows/update-toc.yml) in [.github/workflows](.github/workflows) which you can copy for your own repository for the same functionality. This file will be automatically updated with every release to point toward the current release version of this action. If you would prefer to always be in sync with the main branch of this repository, replace the version number with `main`. 

Table update functionality is handled via the [toc-generator.py](scripts/toc-generator.py) Python (3.x) script in the [scripts](scripts) folder.

If a directory contains a `README.md` file, the directory will appear in the table of contents as a link pointing to the `README.md` file.

If you do not want a directory containing Markdown files to be indexed, simply add a file named `.toc-ignore` to it.

### Options

| Argument | Description | Default Value |
|----------|-------------|---------------|
| `table-file` | The file where the table of contents will be generated or updated | `README.md` |
| `root-path` | The root path to start searching for files | `.` (Current working directory/Root of repository.) |
| `exclude-root` | Whether to exclude the root directory from the table of contents | `false` |
| `file-extension` | The file extension to look for (e.g., "md" for Markdown files) | `.md` |
| `primary-file-name` | The name of the main file to be listed first in the table of contents | `README.md` |
| `toc-start-tag` | The tag that marks the beginning of the table of contents section | `<!-- toc-start -->` |
| `toc-end-tag` | The tag that marks the end of the table of contents section | `<!-- toc-end -->` |
| `toc-ignore-file-name` | The name of a file that, if present, indicates to ignore that directory | `.toc-ignore` |

### Special Tags

You can control how entries appear in the table of contents using special tags near the start of your file. These tags must appear at the start of the file.

These tags can also appear after whitespace or YAML front matter.

For example,

```markdown
---
author: "Some author"
date: "2024-08-09"
--- 

<!-- some-tag: someValue -->
```

and 

```markdown
<!-- some-tag: someValue -->
```

are both valid. 
However,

```markdown
Some random text.

# Some Header

<!-- some-tag: someValue -->
```

is not.

Tags can also be combined.
For example, 

```markdown
<!-- toc-name: SomeName -->
<!-- toc-order: 1 -->
```

will set the entry name in the table of contents to `SomeName` and will set its order to `1` in its group. 

Below you can find the current list of supported tags with examples and descriptions.

| Tag | Example | Description |
| --- | ------- | ----------- |
| toc-name | `<!-- toc-name: Custom Name; -->` | Sets a custom name for this file's entry in the table of contents. If this file is a README.md, the custom name will be applied to the directory listing instead. |
| toc-order | `<!-- toc-order: 1 -->` | Sets the order group of the table of contents item. This dictates the order in which entries appear within the context of their parent directory. Using `last` instead of an integer will result in the entry using the highest possible order group. Any entry that does not explicitly set this will be assigned to the order group immediately before the last one. |
| toc-ignore | `<!-- toc-ignore; -->` | Excludes this file from the table of contents. |

---

[Back to top](#markdown-table-of-contents-generator)
