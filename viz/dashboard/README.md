How to run the dashboard
- Download Anaconda server at: http://continuum.io/downloads
- Install Anaconda: 
  $bash Anaconda-2.1.0-Linux-x86.sh
- Add anaconda bin directory to PATH variable
  Modify ~/.profile or run export PATH=/home/yourusername/anaconda/bin:$PATH) then run $source ~/.profile
- Run the bokeh server: 
  $bokeh-server
- Run the dashboard:
  $python nyu-dashboard.py path_to_data_monitor_directory
