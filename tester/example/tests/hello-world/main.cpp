#include <catch2/catch_test_macros.hpp>

#include "./support-wrap.hpp"

#include <string>
#include <cstdlib>

using namespace std::chrono_literals;
using namespace std::literals::string_literals;



TEST_CASE("Hello world", "[debug][release]") {
    Process p(GetSubmissionPath(), {});

    REQUIRE( p.ReadLine(30s).value_or("") == "Hello world!" );
    p.CloseStdIn();

    REQUIRE(p.Wait(2s) == 0);
}

TEST_CASE("Echo back", "[debug][release]") {
    Process p(GetSubmissionPath(), {"Ahoj APC++ 2021!"});

    REQUIRE( p.ReadLine(30s).value_or("") == "Ahoj APC++ 2021!" );
    p.CloseStdIn();

    REQUIRE(p.Wait(2s) == 0);
}

TEST_CASE("Get data", "[debug][release]") {
    auto file = GetData("input.txt");

    std::ifstream in(file);
    REQUIRE(in.is_open());

    std::string line;
    REQUIRE(std::getline(in, line));

    REQUIRE(line == "Hello world!");
}

TEST_CASE("Cannot modify data", "[debug][release]") {
    auto file = GetData("input.txt");

    std::ofstream out(file);
    REQUIRE(!out.is_open());
}
