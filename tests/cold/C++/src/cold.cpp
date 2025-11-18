/*
Author: Ram Basnet
Date: January 2017
Kattis - Cold-puter Science problem
https://open.kattis.com/problems/cold
*/

#include <iostream>
#include <cstring>
#include <cassert>
#include <string>
#include "util.h"

using namespace std;

void solve();

int main(int argc, char *argv[])
{

    solve();
    return 0;
}

void solve()
{
    int n, t, cold = 0;
    cin >> n;

    for (int i = 0; i < n; i++)
    {
        cin >> t;
        cold += answer(t);
    }
    cout << cold << endl;
}