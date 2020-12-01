# DICOM Tools
> A Python toolkit for parsing and analyzing metadata from DICOM files.


This project utilizes the `pydicom` and `fastcore` libraries. It borrows ideas (and some code) from the `fastai.medical.imaging` library ([source](https://github.com/fastai/fastai/blob/master/fastai/medical/imaging.py)).

The metadata preprocessing and series selection algorithm are recreated from the paper by Gauriau et al. (_reference below_), in which a Random Forest classifier is trained to predict the sequence type (e.g. T1, T2, FLAIR, ...) of series of images from brain MRI. Such a tool may be used to select the appropriate series of images for input into a machine learning pipeline.
> _Reference:_ Gauriau R, et al. Using DICOM Metadata for Radiological Image Series Categorization: a Feasibility Study on Large Clinical Brain MRI Datasets. _Journal of Digital Imaging_. 2020 Jan; 33:747–762. ([link to paper](https://link.springer.com/article/10.1007/s10278-019-00308-x))

## Install

1. `git clone` the repository
2. `cd` into the repo
3. `pip install .` (include the `-e` flag for an editable install)

## How to use

Read a DICOM file:

```python
from pydicom.data import get_testdata_file

path = Path(get_testdata_file("MR_truncated.dcm"))
ds = path.dcmread()
ds.file_meta
```




    (0002, 0000) File Meta Information Group Length  UL: 190
    (0002, 0001) File Meta Information Version       OB: b'\x00\x01'
    (0002, 0002) Media Storage SOP Class UID         UI: MR Image Storage
    (0002, 0003) Media Storage SOP Instance UID      UI: 1.3.6.1.4.1.5962.1.1.4.1.1.20040826185059.5457
    (0002, 0010) Transfer Syntax UID                 UI: Explicit VR Little Endian
    (0002, 0012) Implementation Class UID            UI: 1.3.6.1.4.1.5962.2
    (0002, 0013) Implementation Version Name         SH: 'DCTOOL100'
    (0002, 0016) Source Application Entity Title     AE: 'CLUNIE1'



Import a select subset of DICOM metadata into a `pandas.DataFrame`. The subset is defined in `dicomtools.core` and is based on the metadata used for the series selection algorithm in the paper referenced above.

```python
df = pd.DataFrame.from_dicoms([path]).drop('fname', axis=1)
df.T
```




<div>
<style scoped>
    .dataframe tbody tr th:only-of-type {
        vertical-align: middle;
    }

    .dataframe tbody tr th {
        vertical-align: top;
    }

    .dataframe thead th {
        text-align: right;
    }
</style>
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>0</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>ImageType</th>
      <td>[DERIVED, SECONDARY, OTHER]</td>
    </tr>
    <tr>
      <th>SOPClassUID</th>
      <td>MR Image Storage</td>
    </tr>
    <tr>
      <th>PatientID</th>
      <td>4MR1</td>
    </tr>
    <tr>
      <th>ContrastBolusAgent</th>
      <td></td>
    </tr>
    <tr>
      <th>ScanningSequence</th>
      <td>SE</td>
    </tr>
    <tr>
      <th>SequenceVariant</th>
      <td>NONE</td>
    </tr>
    <tr>
      <th>ScanOptions</th>
      <td></td>
    </tr>
    <tr>
      <th>MRAcquisitionType</th>
      <td>3D</td>
    </tr>
    <tr>
      <th>SliceThickness</th>
      <td>0.8</td>
    </tr>
    <tr>
      <th>RepetitionTime</th>
      <td>4000</td>
    </tr>
    <tr>
      <th>EchoTime</th>
      <td>240</td>
    </tr>
    <tr>
      <th>EchoTrainLength</th>
      <td>None</td>
    </tr>
    <tr>
      <th>StudyInstanceUID</th>
      <td>1.3.6.1.4.1.5962.1.2.4.20040826185059.5457</td>
    </tr>
    <tr>
      <th>SeriesInstanceUID</th>
      <td>1.3.6.1.4.1.5962.1.3.4.1.20040826185059.5457</td>
    </tr>
    <tr>
      <th>StudyID</th>
      <td>4MR1</td>
    </tr>
    <tr>
      <th>SeriesNumber</th>
      <td>1</td>
    </tr>
    <tr>
      <th>AcquisitionNumber</th>
      <td>0</td>
    </tr>
    <tr>
      <th>InstanceNumber</th>
      <td>1</td>
    </tr>
    <tr>
      <th>ImageOrientationPatient</th>
      <td>[1.0000, 0.0000, 0.0000, 0.0000, 1.0000, 0.0000]</td>
    </tr>
    <tr>
      <th>PhotometricInterpretation</th>
      <td>MONOCHROME2</td>
    </tr>
    <tr>
      <th>PixelSpacing</th>
      <td>[0.3125, 0.3125]</td>
    </tr>
  </tbody>
</table>
</div>




<h2 id="Finder" class="doc_header"><code>class</code> <code>Finder</code><a href="https://github.com/wfwiggins/dicomtools/tree/master/dicomtools/series/find.py#L65" class="source_link" style="float:right">[source]</a></h2>

> <code>Finder</code>(**`path`**)

A class for finding DICOM files of a specified sequence type from a specific .



<h4 id="Finder.predict" class="doc_header"><code>Finder.predict</code><a href="https://github.com/wfwiggins/dicomtools/tree/master/dicomtools/series/find.py#L74" class="source_link" style="float:right">[source]</a></h4>

> <code>Finder.predict</code>()

Obtains predictions from the model specified in `model_path`



<h4 id="Finder.find" class="doc_header"><code>Finder.find</code><a href="https://github.com/wfwiggins/dicomtools/tree/master/dicomtools/series/find.py#L86" class="source_link" style="float:right">[source]</a></h4>

> <code>Finder.find</code>(**`plane`**=*`'ax'`*, **`seq`**=*`'t1'`*, **`contrast`**=*`True`*, **`thresh`**=*`0.8`*, **\*\*`kwargs`**)

Returns a `pandas.DataFrame` with predicted sequences matching the query at the specified threshold

