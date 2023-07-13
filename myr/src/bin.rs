fn main() {
    use clap::{Parser, Subcommand};
    use std::path::Path;
    use libmyr as myr;

    #[derive(Parser, Debug)]
    #[command(author, version, about, long_about)]
    #[command(propagate_version = true)]
    struct Cli {
        #[command(subcommand)]
        pub command: Commands,
    }

    #[derive(Subcommand, Debug)]
    enum Commands {
        // This struct lists all the subcommands

        /// Create a new, empty data bundle
        New {
            /// Path to the new data bundle directory
            path: String,
        },
        /// Validate a data bundle, without freezing it
        Validate {
            /// Path to the data bundle directory
            path: String,
        },
        /// Freeze a data bundle, making it immutable
        Freeze {
            /// Path to the data bundle directory
            path: String,
        },
    }

    let cli = Cli::parse();

    match cli.command {
        Commands::New { path } => myr::new_bundle_at(Path::new(&path)),
        Commands::Validate { path } => myr::validate_bundle_at(Path::new(&path)),
        Commands::Freeze { path } => myr::freeze_bundle_at(Path::new(&path)),
    }
}
