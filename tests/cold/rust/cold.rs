// Cold solution in Rust

use std::io::{self, BufRead};

fn main() {
    let stdin = io::stdin();
    let mut lines = stdin.lock().lines();
    let n = lines.next().unwrap().unwrap().parse::<usize>().unwrap();
    let mut a = vec![0; n];
    for i in 0..n {
        a[i] = lines.next().unwrap().unwrap().parse::<i32>().unwrap();
    }
    let mut ans = 0;
    for i in 0..n {
        if a[i] < 0 {
            ans += 1;
        }
    }
    println!("{}", ans);
}