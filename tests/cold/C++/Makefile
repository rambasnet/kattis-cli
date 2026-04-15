SRC = $(wildcard src/*.cpp)

kattis_test:
	g++ -g -O2 -std=gnu++23 -static -lrt -Wl,--whole-archive -lpthread -Wl,--no-whole-archive -o cold.exe $(SRC)
	cat ../data/1.in | ./cold.exe | diff - ../data/1.ans
	cat ../data/2.in | ./cold.exe | diff - ../data/2.ans
	@echo "All tests passed!"

unittest:
	g++ -g -O2 -std=gnu++23 -static -lrt -Wl,--whole-archive -lpthread -Wl,--no-whole-archive -o test_cold.exe src/util.cpp tests/test_util.cpp
	./test_cold.exe

clean:
	rm -f *.exe
	rm -f *.out