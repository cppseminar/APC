package cmd

import  "github.com/spf13/cobra"
import "log"
import "os"

var rootCmd = &cobra.Command{
	Use:   "input-proxy",
	Long: `Input proxy is simple web server that verifies JWS signature and forwards request further.`,
	Run: func(cmd *cobra.Command, args []string) {
	},

  }



var (
	 destination string
	 port uint32
)


func init() {
	rootCmd.Flags().Uint32Var(&port, "port", 0, "Port number on which to run")
	rootCmd.Flags().StringVar(&destination, "url", "", "Destination url to which proxy will forward requests")
	rootCmd.MarkFlagRequired("port")
	rootCmd.MarkFlagRequired("url")
}



// Execute parses command line arguments
func Execute() (uint32, string) {
	if err := rootCmd.Execute(); err != nil {
	  log.Fatal(err.Error())
	}
	// This is not "cobra ideal", but it solves problem with calling -h
	if destination == "" || port == 0 {
		os.Exit(0)
	}

	return port, destination
}
