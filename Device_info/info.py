import psutil
from TextToSpeech.Fast_DF_TTS import speak

def get_ram_info():
    ram = psutil.virtual_memory()
    total_ram = ram.total / (1024 ** 3)  
    available_ram = ram.available / (1024 ** 3)  
    return f"Total RAM: {total_ram:.2f} GB\nAvailable RAM: {available_ram:.2f} GB"

def get_storage_info(drive_letter):
    partition_info = psutil.disk_partitions()
    for partition in partition_info:
        if partition.device.startswith(drive_letter):
            usage = psutil.disk_usage(partition.mountpoint)
            total = usage.total / (1024 ** 3)  
            used = usage.used / (1024 ** 3)    
            free = usage.free / (1024 ** 3)   
            return (f"Drive {drive_letter}:\n"
                    f"Total Storage: {total:.2f} GB\n"
                    f"Used Storage: {used:.2f} GB\n"
                    f"Free Storage: {free:.2f} GB")
    return f"Drive {drive_letter} not found."

def get_info(query):
        if query == "exit":
            speak("Exiting...")
        elif "ram" in query:
            speak(get_ram_info())
        elif "storage" in query:
            drive_letter = query.split()[-1].upper()  
            speak(get_storage_info(drive_letter))
        elif "available storage" in query:
            drive_letter = query.split()[-1].upper()  
            speak(get_storage_info(drive_letter))
        else:
            pass
