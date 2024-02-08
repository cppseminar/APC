#include <catch2/catch_test_macros.hpp>
#include <catch2/benchmark/catch_benchmark.hpp>

#include "./support-wrap.hpp"

#include <string>
#include <cstdlib>

using namespace std::chrono_literals;
using namespace std::literals::string_literals;



TEST_CASE("Zero parameters", "[debug][release]") {
    Process p(GetSubmissionPath(), {});

    REQUIRE( p.ReadLine(30s).value_or("") == "Hello world!" );
    p.CloseStdIn();

    REQUIRE(p.Wait(2s) == 0);
}

TEST_CASE("Leak", "[debug][release]") {
    Process p(GetSubmissionPath(), {"leak"});

    REQUIRE(p.Wait(2s) == 0);
}

TEST_CASE("Addr", "[debug][release]") {
    Process p(GetSubmissionPath(), {"addr"});

    REQUIRE(p.Wait(2s) == 0);
}

TEST_CASE("Addr2", "[debug][release]") {
    Process p(GetSubmissionPath(), {"addr2"});

    REQUIRE(p.Wait(2s) == 0);
}

TEST_CASE("dbg", "[debug][release]") {
    Process p(GetSubmissionPath(), {"dbg"});

    REQUIRE(p.Wait(2s) == 0);
}

TEST_CASE("abort", "[debug][release]") {
    Process p(GetSubmissionPath(), {"abort"});

    REQUIRE(p.Wait(2s) == 0);
}

TEST_CASE("unhandled", "[debug][release]") {
    Process p(GetSubmissionPath(), {"unhandled"});

    REQUIRE(p.Wait(2s) == 0);
}

TEST_CASE("fail", "[debug][release]") {
    Process p(GetSubmissionPath(), {"fail"});

    REQUIRE(p.Wait(2s) == 1);
}

TEST_CASE("afterfree", "[debug][release]") {
    Process p(GetSubmissionPath(), {"afterfree"});

    REQUIRE(p.Wait(2s) == 0);
}

TEST_CASE("Perf test", "[release]") {
    BENCHMARK("Perf test") {
        Process p(GetSubmissionPath(), {"bench"});

        REQUIRE(p.ReadLine(30s).value_or("") == "5050");
        p.CloseStdIn();

        p.Wait(2s);
    };
}