# md-split

```mermaid
%%{init: {'themeVariables': { 'fontFamily': 'Monospace', 'text-align': 'left'}}}%%
flowchart LR
    subgraph in.md
        SRC[# Heading 1<br>x x x x<br><br># Heading 2<br>y y y y<br><br>## Heading 2.1<br>z z z z]
    end
    subgraph in_split/Heading 1.md
        SPLIT_A[# Heading 1<br>x x x x<br><br>]
    end
    subgraph in_split/Heading 2.md
        SPLIT_B[# Heading 2<br>y y y y<br><br>## Heading 2.1<br>z z z z]
    end
    SRC --> MD_SPLIT(md_split in.md)
    MD_SPLIT --> SPLIT_A
    MD_SPLIT --> SPLIT_B
    style SRC text-align:left
    style SPLIT_A text-align:left
    style SPLIT_B text-align:left
    style MD_SPLIT fill:#000,color:#0F0
```

## For Users

**Installation**

Either use pip:

    pip install md-split
    md_split

Or simply download [md_split.py](md_split.py) and run it:

    python3 md_split.py

## For Developers

Run tests

    poetry run pytest

[Download statistics](https://pypistats.org/packages/md-split)