use shellfish::Command;
use shellfish::Shell;
use std::error::Error;
use std::fmt;

fn main() -> Result<(), Box<dyn std::error::Error>> {
    // Define a shell
    let mut shell = Shell::new((),"<[Shellfish Example]>-$ ".to_string());

    // Set the prompt
    //shell.prompt = "<[Shellfish Example]>-$ ".to_string();

    // Add a command
    shell.commands.insert(
        "greet".to_string(),
        Command::new("greets you.".to_string(), greet),
    );

    // Run the shell
    shell.run()?;

    Ok(())
}

/// Greets the user
fn greet(_state: &mut (), args: Vec<String>) -> Result<(), Box<dyn Error>> {
    let arg = args.get(1).ok_or_else(|| Box::new(GreetingError))?;
    println!("Greetings {}, my good friend.", arg);
    Ok(())
}

/// Greeting error
#[derive(Debug)]
pub struct GreetingError;

impl fmt::Display for GreetingError {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        write!(f, "No name specified")
    }
}

impl Error for GreetingError {}