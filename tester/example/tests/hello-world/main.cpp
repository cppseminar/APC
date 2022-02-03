#define CATCH_CONFIG_MAIN
#define CATCH_CONFIG_ENABLE_BENCHMARKING
#include <catch.hpp>
#include "./support-wrap.hpp"

#include <string>
#include <cstdlib>

using namespace std::chrono_literals;
using namespace std::literals::string_literals;



TEST_CASE("Hello world", "[debug]") {
    Process p(GetSubmissionPath(), {});

    REQUIRE( p.ReadLine(30s).value_or("") == "Hello world!" );
    p.CloseStdIn();

    REQUIRE(p.Wait(2s) == 0);
}

TEST_CASE("Echo back", "[debug]") {
    Process p(GetSubmissionPath(), {"Ahoj APC++ 2021!"});

    REQUIRE( p.ReadLine(30s).value_or("") == "Ahoj APC++ 2021!" );
    p.CloseStdIn();

    REQUIRE(p.Wait(2s) == 0);
}

TEST_CASE("Get data", "[debug]") {
    auto file = GetData("input.txt");

    std::ifstream in(file);
    REQUIRE(in.is_open());

    std::string line;
    REQUIRE(std::getline(in, line));

    REQUIRE(line == "Hello world!");
}

TEST_CASE("Cannot modify data", "[debug]") {
    auto file = GetData("input.txt");

    std::ofstream out(file);
    REQUIRE(!out.is_open());
}
