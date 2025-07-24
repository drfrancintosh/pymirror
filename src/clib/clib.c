#define PY_SSIZE_T_CLEAN  // Add this line BEFORE #include <Python.h>
#include <Python.h>
#include <stdlib.h>
#include <string.h>

static PyObject* rgba_to_rgb16(PyObject* self, PyObject* args) {
    const char* rgba;
    Py_ssize_t data_len;
    int width, height;
    
    if (!PyArg_ParseTuple(args, "y#ii", &rgba, &data_len, &width, &height)) {
        return NULL;
    }
    // Convert RGBA to RGB565
    int rgb565_len = width * height * sizeof(unsigned short);
    unsigned short *rgb565 = malloc(rgb565_len);
    if (!rgb565) return NULL;

    for (int i = 0; i < width * height; ++i)
    {
        unsigned char r = rgba[i * 4];
        unsigned char g = rgba[i * 4 + 1];
        unsigned char b = rgba[i * 4 + 2];

        // Convert to RGB565 format
        rgb565[i] = ((r & 0xF8) << 8) | ((g & 0xFC) << 3) | (b >> 3);
    }
    PyObject *result = PyBytes_FromStringAndSize((char*)rgb565, rgb565_len);
    free(rgb565);
    return result;
}

static PyObject* free_rgb16(PyObject* self, PyObject* args) {
    void *rgb565;
    if (!PyArg_ParseTuple(args, "O", &rgb565)) {
        return NULL;
    }
    free(rgb565);
    Py_RETURN_NONE;
}

static PyMethodDef clib_methods[] = {
    {"rgba_to_rgb16", rgba_to_rgb16, METH_VARARGS, "Convert RGBA to RGB565"},
    {"free_rgb16", free_rgb16, METH_VARARGS, "Free RGB565 data"},
    {NULL, NULL, 0, NULL}
};

static struct PyModuleDef clib_module = {
    PyModuleDef_HEAD_INIT,
    "clib",
    "C library for image conversion",
    -1,
    clib_methods
};

// This is the required function name for Python 3
PyMODINIT_FUNC PyInit_clib(void) {
    return PyModule_Create(&clib_module);
}