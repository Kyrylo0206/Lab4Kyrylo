#!/usr/bin/env python3
import subprocess
import sys
import os
import time
import threading

def run_service(script_name, service_name, port):
    print(f" Запуск {service_name} на порту {port}")
    try:
        federation_dir = os.path.join(os.getcwd(), "federation")
        
        process = subprocess.Popen(
            [sys.executable, script_name], 
            cwd=federation_dir,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        print(f" {service_name} запущено (PID: {process.pid})")
        return process
        
    except Exception as e:
        print(f" Помилка запуску {service_name}: {e}")
        return None

def main():
    print("GraphQL Federation - Запуск всіх сервісів")

    if not os.path.exists("federation"):
        print("Переконайтеся, що ви в директорії todo_app-2")
        sys.exit(1)

    services = [
        ("user_server.py", "User Service", 8002),
        ("todo_server.py", "Todo Service", 8003),
        ("gateway.py", "Federation Gateway", 8001)
    ]
    
    processes = []
    
    try:
        for script, name, port in services:
            process = run_service(script, name, port)
            if process:
                processes.append((process, name, port))
                time.sleep(2) 
        
        if not processes:
            print(" Жоден сервіс не вдалося запустити")
            sys.exit(1)
        
        print("🎉 Всі сервіси запущено успішно!")

        for _, name, port in processes:
            print(f"   • {name:20} : http://localhost:{port}/graphql")
        
        print("\n естування федерації:")
        print("1 User Service:")
        print("   query { users { id username email } }")
        print("   http://localhost:8002/graphql")
        
        print("\n2 Todo Service:")
        print("   query { todos { id title user { id } } }")
        print("   http://localhost:8003/graphql")
        
        print("\n3Gateway:")
        print("   query { hello federationInfo }")
        print("   http://localhost:8001/graphql")
        
        print("\nДля перевірки статусу:")
        print("   • http://localhost:8001/ (Gateway info)")
        print("   • http://localhost:8002/ (User service info)")
        print("   • http://localhost:8003/ (Todo service info)")
        
        
        while True:
            time.sleep(1)
            for process, name, port in processes:
                if process.poll() is not None:
        
    except KeyboardInterrupt:
        for process, name, port in processes:
            try:
                process.terminate()
                process.wait(timeout=5)
                print(f"{name} зупинено")
            except subprocess.TimeoutExpired:
                process.kill()
                print(f"{name} примусово зупинено")
            except Exception as e:
                print(f"Помилка зупинки {name}: {e}")
        
        print("Всі федеративні сервіси зупинено")
    
    except Exception as e:
        print(f"Неочікувана помилка: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
