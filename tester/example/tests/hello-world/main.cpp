#define CATCH_CONFIG_MAIN
#define CATCH_CONFIG_ENABLE_BENCHMARKING
#include "./catch.hpp"
#include "./support-wrap.hpp"

#include <string>
#include <cstdlib>

using namespace std::chrono_literals;
using namespace std::literals::string_literals;



TEST_CASE("Hello world", "[example]") {
    Process p(GetSubmissionPath(), {});

    REQUIRE( p.ReadLine(30s).value_or("") == "Hello world!" );
    p.CloseStdIn();

    REQUIRE(p.Wait(2s) == 0);
}

TEST_CASE("Echo back", "[example]") {
    Process p(GetSubmissionPath(), {"Ahoj APC++ 2021!"});

    REQUIRE( p.ReadLine(30s).value_or("") == "Ahoj APC++ 2021!" );
    p.CloseStdIn();

    REQUIRE(p.Wait(2s) == 0);
}
