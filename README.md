# CGC-image-scrapper

## Setup

> Install Dependencies

```bash
pip install mpire tqdm pandas requests wget colorama
```

## Input format

You can download the list of entries from this [webpage](https://isb-cgc.appspot.com/cohorts/filelist/).

Choose the uuid that you want to download and format the file as below

- `Input file` must be in `tsv` format
- `Input file` must have the header `uuid`

| uuid |
| - |
| uuid 1 | 
| uuid 2 | 
| uuid 3 | 
| ... |
| uuid n |

## Usage

```bash
  python scrapper.py --file <Location of uuid file>
```
