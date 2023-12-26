import utils
utils.add_submodules_to_path()

from historicaldate import hdate

def compare(s,re_check=None, dcheck=None, pdcheck=None, dateformat=None, check_days=False):
    hd = hdate.HDate(s, dateformat=dateformat)
    if re_check is not None: # Check output from re
        found = {k:v for k, v in hd.re_parsed.items() if v != re_check.get(k, None)}
        expected = {k:re_check.get(k,None) for k in found}
        assert found == {}, f"re_check mismatches for '{s}': Found {found} Expected {expected}"

    if dcheck is not None: # Check canonical dictionary
        found = {k:v for k, v in hd.d_parsed.items() if v != dcheck.get(k, None)}
        expected = {k:dcheck.get(k,None) for k in found}
        assert found == {}, f"d_parsed mismatches for '{s}': Found {found} Expected {expected}"

    if pdcheck is not None: # Check canonical dictionary
        found = {k:v for k, v in hd.pdates.items() 
                    if ((v != pdcheck.get(k, None)) and (check_days or (k[0:8] != "ordinal_")))}
        expected = {k:pdcheck.get(k,None) for k in found}
        assert found == {}, f"pdate mismatches for '{s}': Found {found} Expected {expected}"

def expect_valueerror(s, dateformat=None):
    try:
        hd = hdate.HDate(s, dateformat=dateformat)
        assert False, f"Illegal date '{s}' has not raised a ValueError"
    except ValueError:
        return True
    
