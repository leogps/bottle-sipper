#!/bin/bash

port=8089

wait_for_server() {
  echo "waiting for server to start..."
      while ! curl -s "http://localhost:$port/" > /dev/null; do
        sleep 0.5  # Wait for 500ms before retrying
      done
    echo "server is up!"
}

bench_http_server() {
  echo "running http-server benchmark..."
  http-server -p $port ./srvr-root &
  pid=$!

  wait_for_server

  echo "running benchmark against jpg file..."
  hs_jpg_bench=$(ab -n 10000 -c 100 "http://localhost:$port/elephant-unsplash.jpg")
  echo "running benchmark against txt file..."
  hs_txt_bench=$(ab -n 10000 -c 100 "http://localhost:$port/hipster-ipsum.txt")
  kill -9 $pid
  export hs_jpg_bench
  export hs_txt_bench
}

bench_bottle_sipper() {
  echo "running bottle-sipper benchmark..."
  ../dist/sipper -p $port -w 50 ./srvr-root &
  pid=$!

  wait_for_server

  echo "running benchmark against jpg file..."
  bs_jpg_bench=$(ab -n 10000 -c 100 "http://localhost:$port/elephant-unsplash.jpg")
  echo "running benchmark against txt file..."
  bs_txt_bench=$(ab -n 10000 -c 100 "http://localhost:$port/hipster-ipsum.txt")
  kill -9 $pid
  export bs_jpg_bench
  export bs_txt_bench
}

setup() {
  lsof -ti:$port | xargs kill -9
}

setup
bench_http_server
setup
bench_bottle_sipper


printf "\n******************************\n"
printf "\n------------------------------\n"
printf "\n ### http-server (jpg) benchmark results ### \n"
echo "$hs_jpg_bench"
printf "\n------------------------------\n"
printf "\n------------------------------\n"
printf "\n ### bottle-server (jpg) benchmark results ### \n"
echo "$bs_jpg_bench"

printf "\n******************************\n"
printf "\n******************************\n"

printf "\n------------------------------\n"
printf "\n ### http-server (txt) benchmark results ### \n"
echo "$hs_txt_bench"
printf "\n------------------------------\n"
printf "\n------------------------------\n"

printf "\n ### bottle-server (txt) benchmark results ### \n"
echo "$bs_txt_bench"
printf "\n------------------------------\n"
printf "\n******************************\n"
printf "\n******************************\n"

