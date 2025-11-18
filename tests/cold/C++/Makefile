SRC = $(wildcard src/*.cpp)

kattis_test:
	g++ -std=c++17 -I src -o cold.exe $(SRC)
	cat ../data/1.in | ./cold.exe | diff - ../data/1.ans
	cat ../data/2.in | ./cold.exe | diff - ../data/2.ans
	@echo "All tests passed!"

unit_test:
	g++ -std=c++17 -o test_cold.exe src/util.cpp tests/test_util.cpp
	./test_cold.exe

clean:
	rm -f *.exe
	rm -f *.out