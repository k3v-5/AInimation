import os
import time
from pathlib import Path

def audit_timeline():
    project_root = Path(r"e:\Disco F\Dev\IANIMATION")
    target_dirs = ["backend", "src", "src-tauri", "scripts", "tests"]
    
    records = []
    for d in target_dirs:
        dp = project_root / d
        if not dp.exists():
            continue
        for root, dirs, files in os.walk(dp):
            if "node_modules" in root or "target" in root or ".git" in root or "__pycache__" in root:
                continue
            for f in files:
                if f.endswith((".py", ".ts", ".tsx", ".rs", ".json", ".toml", ".html", ".css", ".md")):
                    fp = Path(root) / f
                    try:
                        st = fp.stat()
                        records.append({
                            "path": str(fp.relative_to(project_root)),
                            "mtime": st.st_mtime,
                            "ctime": st.st_ctime,
                            "size": st.st_size
                        })
                    except Exception as e:
                        pass
                        
    records.sort(key=lambda r: r["mtime"])
    
    print(f"Total source/test/doc files scanned: {len(records)}")
    if records:
        earliest = records[0]["mtime"]
        latest = records[-1]["mtime"]
        span_seconds = latest - earliest
        print(f"Earliest file mtime: {time.strftime('%Y-%m-%d %H:%M:%S UTC', time.gmtime(earliest))}")
        print(f"Latest file mtime:   {time.strftime('%Y-%m-%d %H:%M:%S UTC', time.gmtime(latest))}")
        print(f"Total span: {span_seconds:.1f} seconds ({span_seconds/3600:.2f} hours)")
        
        # Check clustering: are all files created within 2 seconds?
        if span_seconds < 10:
            print("ALERT: Suspicious time clustering (< 10 seconds total span)!")
        else:
            print("Time span shows progressive development over time.")
            
        print("\nEarliest 10 files:")
        for r in records[:10]:
            t_str = time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(r['mtime']))
            print(f"  {t_str} | {r['size']:8d} B | {r['path']}")
            
        print("\nLatest 10 files:")
        for r in records[-10:]:
            t_str = time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(r['mtime']))
            print(f"  {t_str} | {r['size']:8d} B | {r['path']}")

    # Check swarm workspace logs
    teamwork_dir = project_root / ".agents" / "teamwork"
    subdirs = [p for p in teamwork_dir.iterdir() if p.is_dir()]
    print(f"\nTotal teamwork agent workspaces: {len(subdirs)}")
    
    # Check for handoffs and progress in milestones
    milestone_names = ["m1", "m2", "m3", "m4", "m5", "m6", "m7"]
    for m in milestone_names:
        matching = [d.name for d in subdirs if m in d.name.lower()]
        print(f"  Milestone {m} agents: {len(matching)} workspace(s) -> {matching[:4]}")

if __name__ == "__main__":
    audit_timeline()
