pub fn parse_config(input: &str) -> i32 {
    let parts: Vec<&str> = input.split('=').collect();
    if parts.len() != 2 {
        return -1; // invalid format
    }
    let key = parts[0];
    let value = parts[1];
    if key == "threads" {
        // BUG: unwrap will panic if value is not an integer
        return value.parse::<i32>().unwrap();
    }
    -1
}

#[cfg(test)]
mod tests {
    use super::*;
    #[test]
    fn smoke() {
        let _ = parse_config("threads=4");
    }
}
