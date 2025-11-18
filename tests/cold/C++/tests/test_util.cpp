// make sure to define DOCTEST_CONFIG_IMPLEMENT_WITH_MAIN in only one cpp before including doctest.h
#define DOCTEST_CONFIG_IMPLEMENT_WITH_MAIN
#include "../../../doctest/doctest.h"
#include "../src/util.h"


TEST_CASE("test answer function")
{
    CHECK(answer(-100000) == 1);
    CHECK(answer(1000000) == 0);
    CHECK(answer(0) == 0);
}