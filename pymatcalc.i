%module pymatcalc

%feature("autodoc", "1");

%{
#define SWIG_FILE_WITH_INIT
#include "matcalc_api.h"
%}

%include exception.i

%exception {
    try {
        $action
    } catch(const std::exception& e) {
        SWIG_exception(SWIG_RuntimeError, e.what());
    } catch(...) {
        SWIG_exception(SWIG_RuntimeError, "Unknown exception");
    }
}

%include "matcalc_api.h"
