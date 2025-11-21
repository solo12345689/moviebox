try:
    with open('import_log.txt', 'w') as f:
        f.write("Starting import...\n")
    import moviebox_api
    with open('import_log.txt', 'a') as f:
        f.write("Import successful\n")
except Exception as e:
    with open('import_log.txt', 'a') as f:
        f.write(f"Import failed: {e}\n")
