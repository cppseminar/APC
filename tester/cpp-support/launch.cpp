#include <catch2/catch_session.hpp>

// explicitly defining main here is needed because sometimes
// it happened, that student will include main in submission,
// it is not a problem for testing whole applications (it is in 
// fact required :)), but for true unittest, where student 
// just need to provide some classes and functions this is 
// problematic, since linker will prefer this main instead
// if one provided by catch2
//
// NOTE: it was OK, when catch2 was just a header, because
// then the main will be redefinition, but they change the 
// library to be more like standard library, so main is not
// provided during compilation, but rather in the link phase
int main(int argc, char* argv[]) {
  Catch::Session session; // There must be exactly one instance

  // writing to session.configData() here sets defaults
  // this is the preferred way to set them

  int returnCode = session.applyCommandLine(argc, argv);
  if (returnCode != 0) // Indicates a command line error
        return returnCode;

  // writing to session.configData() or session.Config() here
  // overrides command line args
  // only do this if you know you need to

  int numFailed = session.run();

  // numFailed is clamped to 255 as some unices only use the lower 8 bits.
  // This clamping has already been applied, so just return it here
  // You can also do any post run clean-up here
  return numFailed;
}