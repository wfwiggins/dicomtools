# AUTOGENERATED! DO NOT EDIT! File to edit: 01_preproc.ipynb (unless otherwise specified).

__all__ = ['exclude_other', 'get_series_fp', 'compute_plane', 'detect_contrast', 'rm_extra_info', 'extract_labels',
           'make_binary_cols', 'rescale_cols', 'get_dummies', 'preprocess']

# Cell
from .basics import *
from .core import *

from sklearn.preprocessing import MinMaxScaler
from sklearn.preprocessing import MultiLabelBinarizer

# Cell
def exclude_other(df):
    other = ['SPINE', 'CSPINE']
    filt = df.BodyPartExamined.isin(other)
    filt1 = df.SOPClassUID == "MR Image Storage"
    df1 = df[~filt].copy()
    return df1[filt1].reset_index(drop=True)


# Cell
def get_series_fp(fn): return Path(fn).parent

# Cell
def compute_plane(row):
    '''
    Computes the plane of imaging from the direction cosines provided in the `ImageOrientationPatient` field.
    The format of the values in this field is: `[x1, y1, z1, x2, y2, z2]`,
    which correspond to the direction cosines for the first row and column of the image pixel data.
    '''
    planes = ['sag', 'cor', 'ax']
    if 'ImageOrientationPatient1' in row.keys():
        dircos = [v for k,v in row.items() if 'ImageOrientationPatient' in k]
    else:
        dircos = row['ImageOrientationPatient']
    dircos = np.array(dircos).reshape(2,3)
    pnorm = abs(np.cross(dircos[0], dircos[1]))
    return planes[np.argmax(pnorm)]


# Cell
_c = re.compile(r'(\+-?c|post)')

# Cell
def detect_contrast(row):
    if _c.search(row['SeriesDescription'].lower()): return 1
    c = row['ContrastBolusAgent']
    if type(c) == str: return 1
    return 0


# Cell
_re_extra_info = re.compile(r'[<([].*?[\])>]')


# Cell
def rm_extra_info(t):
    "Remove extraneous info in closures"
    return _re_extra_info.sub('', t).strip()


# Cell
_t1 = re.compile(r't1')
_spgr = re.compile(r'spgr|mprage')
_t2 = re.compile(r't2')
_flair = re.compile(r'flair')
_swi = re.compile(r'swi|gre|susc|mag|pha|sw')
_adc = re.compile(r'adc|apparent')
_eadc = re.compile(r'exp|eadc')
_dwi = re.compile(r'diff|dwi|trace')
_mra = re.compile(r'mra|angio|cow|tof|mip')
_loc = re.compile(r'loc|scout')


# Cell
def _find_seq(sd):
    if _t1.search(sd):
        if _spgr.search(sd): return 'spgr'
        else: return 't1'
    if _spgr.search(sd): return 'spgr'
    if _t2.search(sd):
        if _flair.search(sd): return 'flair'
        elif _swi.search(sd): return 'swi'
        else: return 't2'
    if _flair.search(sd): return 'flair'
    if _swi.search(sd): return 'swi'
    if _adc.search(sd):
        if _eadc.search(sd): return 'other'
        else: return 'adc'
    if _dwi.search(sd):
        if _eadc.search(sd): return 'other'
        else: return 'dwi'
    if _mra.search(sd): return 'mra'
    if _loc.search(sd): return 'loc'
    return 'unknown'


# Cell
def _extract_label(sd):
    t = rm_extra_info(sd.lower())
    return _find_seq(t)


# Cell
def extract_labels(df):
    "Extract candidate labels from Series Descriptions and computed plane"
    df1 = df[['fname', 'SeriesDescription']].copy()
    df1['fname'] = df1.fname.apply(get_series_fp)
    df1['plane'] = df.apply(compute_plane, axis=1)
    df1['seq_label'] = df1.SeriesDescription.apply(_extract_label)
    df1['contrast'] = df.apply(detect_contrast, axis=1)
    return df1


# Cell
_keep = [
    'fname',
    'SeriesDescription',
    'ImageOrientationPatient',
    'ScanningSequence',
    'SequenceVariant',
    'ScanOptions',
    'MRAcquisitionType',
    'AngioFlag',
    'SliceThickness',
    'RepetitionTime',
    'EchoTime',
    'EchoTrainLength',
    'PixelSpacing',
    'ContrastBolusAgent',
    'InversionTime',
    'DiffusionBValue'
]

_dummies = [
    'ScanningSequence',
    'SequenceVariant',
    'ScanOptions'
]

_d_prefixes = [
    'seq',
    'var',
    'opt'
]

_binarize = [
    'MRAcquisitionType',
    'AngioFlag',
    'ContrastBolusAgent',
    'DiffusionBValue'
]

_rescale = [
    'SliceThickness',
    'RepetitionTime',
    'EchoTime',
    'EchoTrainLength',
    'PixelSpacing',
    'InversionTime'
]

# Cell
def _make_col_binary(df, col):
    s = df[col].isna()
    if any(s):
        df[col] = s.apply(lambda x: 0 if x else 1)
    else:
        targ = df.loc[0, col]
        df[col] = df[col].apply(lambda x: 0 if x == targ else 1)


# Cell
def make_binary_cols(df, cols):
    df1 = df.copy()
    for col in cols:
        _make_col_binary(df1, col)
    return df1


# Cell
def rescale_cols(df, cols):
    df1 = df.copy()
    scaler = MinMaxScaler()
    df1[cols] = scaler.fit_transform(df1[cols])
    return df1.fillna(0)


# Cell
def get_dummies(df, cols, prefix=None):
    df1 = df.copy()
    for i, col in enumerate(cols):
        df1[col].fillna('NONE', inplace=True)
        mlb = MultiLabelBinarizer()
        df1 = df1.join(
            pd.DataFrame(mlb.fit_transform(df1.pop(col)), columns=mlb.classes_).add_prefix(f'{prefix[i]}_')
        )
    return df1


# Cell
_features = ['MRAcquisitionType', 'AngioFlag', 'SliceThickness', 'RepetitionTime',
       'EchoTime', 'EchoTrainLength', 'PixelSpacing', 'ContrastBolusAgent',
       'InversionTime', 'DiffusionBValue', 'seq_E', 'seq_EP', 'seq_G',
       'seq_GR', 'seq_I', 'seq_IR', 'seq_M', 'seq_P', 'seq_R', 'seq_S',
       'seq_SE', 'var_E', 'var_K', 'var_MP', 'var_MTC', 'var_N', 'var_O',
       'var_OSP', 'var_P', 'var_S', 'var_SK', 'var_SP', 'var_SS', 'var_TOF',
       'opt_1', 'opt_2', 'opt_A', 'opt_ACC_GEMS', 'opt_B', 'opt_C', 'opt_D',
       'opt_E', 'opt_EDR_GEMS', 'opt_EPI_GEMS', 'opt_F', 'opt_FAST_GEMS',
       'opt_FC', 'opt_FC_FREQ_AX_GEMS', 'opt_FC_SLICE_AX_GEMS',
       'opt_FILTERED_GEMS', 'opt_FR_GEMS', 'opt_FS', 'opt_FSA_GEMS',
       'opt_FSI_GEMS', 'opt_FSL_GEMS', 'opt_FSP_GEMS', 'opt_FSS_GEMS', 'opt_G',
       'opt_I', 'opt_IFLOW_GEMS', 'opt_IR', 'opt_IR_GEMS', 'opt_L', 'opt_M',
       'opt_MP_GEMS', 'opt_MT', 'opt_MT_GEMS', 'opt_NPW', 'opt_P', 'opt_PFF',
       'opt_PFP', 'opt_PROP_GEMS', 'opt_R', 'opt_RAMP_IS_GEMS', 'opt_S',
       'opt_SAT1', 'opt_SAT2', 'opt_SAT_GEMS', 'opt_SEQ_GEMS', 'opt_SP',
       'opt_T', 'opt_T2FLAIR_GEMS', 'opt_TRF_GEMS', 'opt_VASCTOF_GEMS',
       'opt_VB_GEMS', 'opt_W', 'opt_X', 'opt__']

# Cell
def preprocess(df, keepers=_keep, dummies=_dummies, d_prefixes=_d_prefixes, binarize=_binarize, rescale=_rescale):
    df1 = exclude_other(df)
    df1 = df1[keepers]
    df1['PixelSpacing'] = df1['PixelSpacing'].apply(lambda x: x[0])
    df1 = get_dummies(df1, dummies, d_prefixes)
    df1 = make_binary_cols(df1, binarize)
    df1 = rescale_cols(df1, rescale)
    for f in _features:
        if f not in df1.columns:
            df1[f] = 0
    return df1
