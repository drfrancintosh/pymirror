import ctypes

# A. Create library
C_library = ctypes.CDLL("clib.so")

# B. Specify function signatures
hello_fxn = C_library.say_hello
hello_fxn.argtypes = [ctypes.c_int]

rgba_to_rgb16 = C_library.rgba_to_rgb16
rgba_to_rgb16.argtypes = [ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int, ctypes.c_int]
rgba_to_rgb16.restype = ctypes.POINTER(ctypes.c_ushort)

free_rgb16 = C_library.free_rgb16
free_rgb16.argtypes = [ctypes.POINTER(ctypes.c_ushort)]
free_rgb16.restype = None

# # C. Invoke function
# num_repeats = 5
# hello_fxn(num_repeats)
