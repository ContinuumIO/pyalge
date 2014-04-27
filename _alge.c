#include <Python.h>

#if PY_MAJOR_VERSION >= 3
  #define MOD_ERROR_VAL NULL
  #define MOD_SUCCESS_VAL(val) val
  #define MOD_INIT(name) PyMODINIT_FUNC PyInit_##name(void)
  #define MOD_DEF(ob, name, doc, methods) { \
          static struct PyModuleDef moduledef = { \
            PyModuleDef_HEAD_INIT, name, doc, -1, methods, }; \
          ob = PyModule_Create(&moduledef); }
  #define MOD_INIT_EXEC(name) PyInit_##name();
#else
  #define MOD_ERROR_VAL
  #define MOD_SUCCESS_VAL(val)
  #define MOD_INIT(name) PyMODINIT_FUNC init##name(void)
  #define MOD_DEF(ob, name, doc, methods) \
          ob = Py_InitModule3(name, methods, doc);
  #define MOD_INIT_EXEC(name) init##name();
  #define PyBytes_AS_STRING PyString_AS_STRING
  #define PyBytes_GET_SIZE PyString_GET_SIZE
  #define PyBytes_CheckExact PyString_CheckExact
#endif


/**
<type check> object
<enter>
<exit>
<skipped>
<capture> object:string
**/

typedef enum {
    CODE_NIL=0,
    CODE_TYPECHECK,
    CODE_ENTER,
    CODE_EXIT,
    CODE_SKIPPED,
    CODE_CAPTURE,
} CODE_ENUM;


/*
Implements a simple stack machine to speedup the pattern matching.
*/
static
PyObject* match(PyObject *self, PyObject *args) {
    PyObject *bytecode, *val, *cap, *tmp;
    Py_ssize_t sz, ip;
    int stacksz;
    PyObject* *code;
    PyObject** stack;
    PyObject* stackstack[8];
    unsigned sp = 0;

    #define PUSH(X) stack[sp++]=X
    #define POP() stack[--sp]
    #define TOP() stack[sp - 1]

    if (!PyArg_ParseTuple(args, "OOOi", &bytecode, &val, &cap, &stacksz)) {
        goto ERROR;
    }

    if (!PyBytes_CheckExact(bytecode)){
        PyErr_SetString(PyExc_TypeError, "bytecode is not string/bytes");
        goto ERROR;
    }

    if (stacksz * sizeof(PyObject*) < sizeof(stackstack)) {
        stack = stackstack;
    } else {
        stack = malloc(stacksz * sizeof(PyObject*));
    }

    code = (PyObject**)PyBytes_AS_STRING(bytecode);
    PUSH(val);       /* push initial value */

    sz = PyBytes_GET_SIZE(bytecode) / sizeof(PyObject*);

    for (ip = 0; ip < sz; ++ip) {
        switch ((CODE_ENUM)code[ip]) {
        case CODE_TYPECHECK:
            tmp = code[++ip];
            switch (PyObject_IsInstance(TOP(), tmp)){
            case 1:
                break;
            case 0:
                Py_RETURN_FALSE;
            default:
                goto ERROR;
            }
            break;

        case CODE_ENTER:
            {
                /*
                Unpack the datatype object and put all elements in reverse
                order into the stack
                */
                PyObject *iter, *tos;
                Py_ssize_t vecsz, j, expected_size;

                expected_size = (Py_ssize_t)code[++ip];

                tos = TOP();
                vecsz = PyObject_Size(tos);

                if (vecsz != expected_size) {
                    Py_RETURN_FALSE;
                }

                if (!(iter = PyObject_GetIter(tos))) {
                    goto ERROR;
                }

                j = vecsz - 1;
                while((tmp = PyIter_Next(iter))) {
                    stack[sp + j] = tmp;
                    j -= 1;
                    Py_DECREF(tmp);
                }
                Py_DECREF(iter);
                sp += vecsz;

                if (PyErr_Occurred()) {
                    goto ERROR;
                }
            }
            break;

        case CODE_EXIT:
        case CODE_SKIPPED:
        case CODE_CAPTURE:
            tmp = POP();
            if (NULL == tmp) {
                PyErr_SetString(PyExc_ValueError, "nil on stack");
                goto ERROR;
            }

            if (CODE_CAPTURE == (CODE_ENUM)code[ip]) {
                if (-1 == PyDict_SetItem(cap, code[++ip], tmp)) {
                    goto ERROR;
                }
            }
            break;

        default:
            PyErr_SetString(PyExc_RuntimeError, "invalid opcode");
            goto ERROR;
        }
    }

    Py_RETURN_TRUE;

ERROR:
    if (stackstack != stack) {
        free(stack);
    }
    return NULL;
}


static PyMethodDef ext_methods[] = {
#define declmethod(func) { #func , ( PyCFunction )func , METH_VARARGS , NULL }
    declmethod(match),
    { NULL },
#undef declmethod
};

MOD_INIT(_alge) {
    PyObject *module, *codes;

    MOD_DEF(module, "_alge", "No docs", ext_methods)
    if (!module) {
        return MOD_ERROR_VAL;
    }

    codes = Py_BuildValue("(iiiii)", CODE_TYPECHECK, CODE_ENTER, CODE_EXIT,
                    CODE_SKIPPED, CODE_CAPTURE);
    PyObject_SetAttrString(module, "codes", codes);
    return MOD_SUCCESS_VAL(module);
}

