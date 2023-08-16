#----------------------------------------------------------------
# Generated CMake target import file for configuration "Release".
#----------------------------------------------------------------

# Commands may need to know the format version.
set(CMAKE_IMPORT_FILE_VERSION 1)

# Import target "unity::framework" for configuration "Release"
set_property(TARGET unity::framework APPEND PROPERTY IMPORTED_CONFIGURATIONS RELEASE)
set_target_properties(unity::framework PROPERTIES
  IMPORTED_LINK_INTERFACE_LANGUAGES_RELEASE "C"
  IMPORTED_LOCATION_RELEASE "${_IMPORT_PREFIX}/lib/unity.lib"
  )

list(APPEND _IMPORT_CHECK_TARGETS unity::framework )
list(APPEND _IMPORT_CHECK_FILES_FOR_unity::framework "${_IMPORT_PREFIX}/lib/unity.lib" )

# Commands beyond this point should not need to know the version.
set(CMAKE_IMPORT_FILE_VERSION)
