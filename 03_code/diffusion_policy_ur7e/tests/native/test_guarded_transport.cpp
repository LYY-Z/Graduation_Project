// Local loopback sockets only; no UR protocol handshake or hardware connection.
#include <ur_rtde/rtde.h>
#include <arpa/inet.h>
#include <sys/socket.h>
#include <unistd.h>
#include <chrono>
#include <cstring>
#include <iostream>
#include <stdexcept>
#include <thread>

struct Listener {
  int fd;
  unsigned short port;
  Listener() {
    fd = ::socket(AF_INET, SOCK_STREAM, 0);
    sockaddr_in address{};
    address.sin_family = AF_INET;
    address.sin_addr.s_addr = htonl(INADDR_LOOPBACK);
    if (::bind(fd, reinterpret_cast<sockaddr*>(&address), sizeof(address)) != 0 || ::listen(fd, 1) != 0)
      throw std::runtime_error("loopback listener setup failed");
    socklen_t size = sizeof(address);
    ::getsockname(fd, reinterpret_cast<sockaddr*>(&address), &size);
    port = ntohs(address.sin_port);
  }
  ~Listener() { ::close(fd); }
};

int main() {
  {
    Listener listener;
    std::string received;
    std::thread peer([&] {
      int client = ::accept(listener.fd, nullptr, nullptr);
      char data[8];
      std::size_t total = 0;
      while (total < sizeof(data)) {
        ssize_t count = ::recv(client, data + total, sizeof(data) - total, 0);
        if (count <= 0) break;
        total += count;
      }
      received.assign(data, total);
      ::close(client);
    });
    ur_rtde::RTDE client("127.0.0.1", listener.port, false);
    client.connect();
    client.sendAll(85, "hello");
    client.disconnect(false);
    peer.join();
    if (received.size() != 8 || static_cast<unsigned char>(received[1]) != 8 ||
        received[2] != 85 || received.substr(3) != "hello")
      throw std::runtime_error("normal packet differs from its original payload");
    std::cout << "PASS normal packet preserved" << std::endl;
  }
  {
    Listener listener;
    std::thread peer([&] {
      int client = ::accept(listener.fd, nullptr, nullptr);
      int small = 1024;
      ::setsockopt(client, SOL_SOCKET, SO_RCVBUF, &small, sizeof(small));
      std::this_thread::sleep_for(std::chrono::seconds(3));
      ::close(client);
    });
    ur_rtde::RTDE client("127.0.0.1", listener.port, false);
    client.connect();
    bool failed = false;
    double duration = 0;
    for (int i = 0; i < 500 && !failed; ++i) {
      auto start = std::chrono::steady_clock::now();
      try { client.sendAll(85, std::string(60000, 'x')); }
      catch (const std::runtime_error&) { failed = true; }
      duration = std::chrono::duration<double>(std::chrono::steady_clock::now() - start).count();
    }
    bool immediate_failed = false;
    double immediate_duration = 0;
    for (int i = 0; i < 500 && !immediate_failed; ++i) {
      auto immediate_start = std::chrono::steady_clock::now();
      try { client.sendAll(85, std::string(60000, 'y'), true); }
      catch (const std::runtime_error&) { immediate_failed = true; }
      double elapsed = std::chrono::duration<double>(std::chrono::steady_clock::now() - immediate_start).count();
      if (elapsed > immediate_duration) immediate_duration = elapsed;
    }
    client.disconnect(false);
    peer.join();
    if (!failed || duration > 0.9 || !immediate_failed || immediate_duration > 0.05)
      throw std::runtime_error("backpressure did not fail within bounded send deadline");
    std::cout << "PASS blocked write failed in " << duration << " seconds; no reconnect" << std::endl;
    std::cout << "PASS immediate motion write refused backpressure in " << immediate_duration << " seconds" << std::endl;
  }
}
