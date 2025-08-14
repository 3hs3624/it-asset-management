import tkinter as tk
from tkinter import ttk, messagebox
from tkcalendar import DateEntry
from PS_asset_manager import ITAssetManager
import logging
from datetime import datetime
import sys

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ITAssetManagerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("IT Asset Manager (PostgreSQL)")
        self.root.geometry("1200x700")
        
        # 자산 매니저 초기화
        try:
            self.manager = ITAssetManager()
            logger.info("Asset manager initialized successfully")
        except Exception as e:
            messagebox.showerror("Database Error", f"데이터베이스 연결에 실패했습니다:\n{str(e)}")
            logger.error(f"Failed to initialize asset manager: {e}")
            sys.exit(1)
        
        self.setup_ui()
        self.refresh_treeview()
        self.load_statistics()
    
    def setup_ui(self):
        """UI 구성요소를 설정합니다."""
        # 메인 프레임
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        # 상단 통계 프레임
        self.setup_statistics_frame(main_frame)
        
        # 검색 프레임
        self.setup_search_frame(main_frame)
        
        # 트리뷰 프레임
        self.setup_treeview_frame(main_frame)
        
        # 버튼 프레임
        self.setup_button_frame(main_frame)
    
    def setup_statistics_frame(self, parent):
        """통계 정보를 표시하는 프레임을 설정합니다."""
        stats_frame = ttk.LabelFrame(parent, text="자산 통계", padding=10)
        stats_frame.pack(fill='x', pady=(0, 10))
        
        # 통계 레이블들
        self.stats_labels = {}
        stats_fields = [
            ('total', '총 자산 수'),
            ('hardware', '하드웨어'),
            ('software', '소프트웨어'),
            ('network', '네트워크'),
            ('storage', '스토리지'),
            ('in_stock', '입고'),
            ('waiting', '대기'),
            ('operating', '운영'),
            ('idle', '유휴'),
            ('disposed', '폐기')
        ]
        
        for i, (key, label) in enumerate(stats_fields):
            row = i // 5
            col = i % 5
            
            ttk.Label(stats_frame, text=f"{label}:").grid(row=row, column=col*2, sticky='w', padx=(0, 5))
            self.stats_labels[key] = ttk.Label(stats_frame, text="0", font=('Arial', 10, 'bold'))
            self.stats_labels[key].grid(row=row, column=col*2+1, sticky='w', padx=(0, 20))
    
    def setup_search_frame(self, parent):
        """검색 프레임을 설정합니다."""
        search_frame = ttk.LabelFrame(parent, text="자산 검색", padding=10)
        search_frame.pack(fill='x', pady=(0, 10))
        
        # 검색 필드 선택
        ttk.Label(search_frame, text="검색 필드:").pack(side='left', padx=(0, 5))
        self.search_field_var = tk.StringVar(value="all")
        search_field_combo = ttk.Combobox(search_frame, textvariable=self.search_field_var, 
                                        values=["all", "asset_type", "model", "status", "location"], 
                                        state="readonly", width=15)
        search_field_combo.pack(side='left', padx=(0, 10))
        
        # 검색어 입력
        ttk.Label(search_frame, text="검색어:").pack(side='left', padx=(0, 5))
        self.search_entry = ttk.Entry(search_frame, width=30)
        self.search_entry.pack(side='left', padx=(0, 10))
        
        # 검색 버튼
        search_button = ttk.Button(search_frame, text="검색", command=self.search_assets)
        search_button.pack(side='left', padx=(0, 10))
        
        # 전체 보기 버튼
        clear_search_button = ttk.Button(search_frame, text="전체 보기", command=self.clear_search)
        clear_search_button.pack(side='left')
    
    def setup_treeview_frame(self, parent):
        """트리뷰 프레임을 설정합니다."""
        tree_frame = ttk.Frame(parent)
        tree_frame.pack(fill='both', expand=True, pady=(0, 10))
        
        # 트리뷰 생성
        columns = ("ID", "Type", "Model", "Purchase Date", "Warranty", "Status", "Location", "Reason")
        self.tree = ttk.Treeview(tree_frame, columns=columns, show="headings", height=15)
        
        # 컬럼 설정
        column_widths = {
            "ID": 50, "Type": 80, "Model": 150, "Purchase Date": 100,
            "Warranty": 100, "Status": 80, "Location": 120, "Reason": 200
        }
        
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=column_widths.get(col, 100), anchor='center')
        
        # 스크롤바
        tree_scroll_y = ttk.Scrollbar(tree_frame, orient="vertical", command=self.tree.yview)
        tree_scroll_x = ttk.Scrollbar(tree_frame, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=tree_scroll_y.set, xscrollcommand=tree_scroll_x.set)
        
        # 배치
        self.tree.grid(row=0, column=0, sticky='nsew')
        tree_scroll_y.grid(row=0, column=1, sticky='ns')
        tree_scroll_x.grid(row=1, column=0, sticky='ew')
        
        tree_frame.grid_rowconfigure(0, weight=1)
        tree_frame.grid_columnconfigure(0, weight=1)
        
        # 더블클릭 이벤트
        self.tree.bind("<Double-1>", self.on_tree_double_click)
    
    def setup_button_frame(self, parent):
        """버튼 프레임을 설정합니다."""
        button_frame = ttk.Frame(parent)
        button_frame.pack(fill='x')
        
        # 왼쪽 버튼들
        left_buttons = ttk.Frame(button_frame)
        left_buttons.pack(side='left')
        
        add_button = ttk.Button(left_buttons, text="자산 추가", command=self.on_add_asset)
        add_button.pack(side='left', padx=(0, 10))
        
        update_button = ttk.Button(left_buttons, text="자산 수정", command=self.on_update_asset)
        update_button.pack(side='left', padx=(0, 10))
        
        delete_button = ttk.Button(left_buttons, text="자산 삭제", command=self.on_delete_asset)
        delete_button.pack(side='left', padx=(0, 10))
        
        # 오른쪽 버튼들
        right_buttons = ttk.Frame(button_frame)
        right_buttons.pack(side='right')
        
        refresh_button = ttk.Button(right_buttons, text="새로고침", command=self.refresh_treeview)
        refresh_button.pack(side='right', padx=(10, 0))
        
        export_button = ttk.Button(right_buttons, text="내보내기", command=self.export_data)
        export_button.pack(side='right', padx=(10, 0))
    
    def search_assets(self):
        """자산을 검색합니다."""
        search_term = self.search_entry.get().strip()
        if not search_term:
            messagebox.showwarning("경고", "검색어를 입력해주세요.")
            return
        
        try:
            search_field = self.search_field_var.get()
            if search_field == "all":
                assets = self.manager.search_assets(search_term)
            else:
                assets = self.manager.search_assets(search_term, search_field)
            
            self.display_assets(assets)
            messagebox.showinfo("검색 완료", f"'{search_term}' 검색 결과: {len(assets)}개 자산")
            
        except Exception as e:
            messagebox.showerror("검색 오류", f"검색 중 오류가 발생했습니다:\n{str(e)}")
            logger.error(f"Search error: {e}")
    
    def clear_search(self):
        """검색을 초기화하고 전체 자산을 표시합니다."""
        self.search_entry.delete(0, tk.END)
        self.search_field_var.set("all")
        self.refresh_treeview()
    
    def display_assets(self, assets):
        """트리뷰에 자산 목록을 표시합니다."""
        # 기존 항목 삭제
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # 새 항목 추가
        for asset_id, asset_data in assets.items():
            self.tree.insert("", "end", iid=asset_id, values=(
                asset_id,
                asset_data["Type"],
                asset_data["Model"],
                asset_data["Purchase Date"],
                asset_data["Warranty"],
                asset_data["Status"],
                asset_data["Location"],
                asset_data["Reason"]
            ))
    
    def refresh_treeview(self):
        """트리뷰를 새로고침합니다."""
        try:
            assets = self.manager.list_assets()
            self.display_assets(assets)
            self.load_statistics()
        except Exception as e:
            messagebox.showerror("오류", f"데이터를 불러오는 중 오류가 발생했습니다:\n{str(e)}")
            logger.error(f"Error refreshing treeview: {e}")
    
    def load_statistics(self):
        """통계 정보를 로드합니다."""
        try:
            stats = self.manager.get_asset_statistics()
            for key, label in self.stats_labels.items():
                value = stats.get(key, 0)
                label.config(text=str(value))
        except Exception as e:
            logger.error(f"Error loading statistics: {e}")
    
    def on_tree_double_click(self, event):
        """트리뷰 더블클릭 이벤트"""
        selected_item = self.tree.focus()
        if selected_item:
            self.on_update_asset()
    
    def on_add_asset(self):
        """자산 추가 다이얼로그를 엽니다."""
        self.manage_asset_dialog("자산 추가")
    
    def on_update_asset(self):
        """자산 수정 다이얼로그를 엽니다."""
        selected_item = self.tree.focus()
        if not selected_item:
            messagebox.showerror("오류", "수정할 자산을 선택해주세요.")
            return
        self.manage_asset_dialog("자산 수정", asset_id=int(selected_item))
    
    def on_delete_asset(self):
        """자산 삭제를 확인합니다."""
        selected_item = self.tree.focus()
        if not selected_item:
            messagebox.showerror("오류", "삭제할 자산을 선택해주세요.")
            return
        
        if messagebox.askyesno("확인", "선택한 자산을 삭제하시겠습니까?"):
            try:
                self.manager.delete_asset(int(selected_item))
                self.refresh_treeview()
                messagebox.showinfo("완료", "자산이 삭제되었습니다.")
            except Exception as e:
                messagebox.showerror("오류", f"자산 삭제 중 오류가 발생했습니다:\n{str(e)}")
                logger.error(f"Error deleting asset: {e}")
    
    def manage_asset_dialog(self, title, asset_id=None):
        """자산 관리 다이얼로그를 엽니다."""
        dialog = tk.Toplevel(self.root)
        dialog.title(title)
        dialog.geometry("500x400")
        dialog.transient(self.root)
        dialog.grab_set()
        
        # 폼 필드들
        form_fields = [
            ("Type", "Type", ["HW", "SW", "NW", "STORAGE"]),
            ("Model", "Model", None),
            ("Purchase Date", "Purchase Date", None),
            ("Warranty", "Warranty", None),
            ("Status", "Status", ["입고", "대기", "운영", "유휴", "폐기"]),
            ("Location", "Location", ["본사 서버실", "개인지급", "프로젝트장소", "기타"]),
            ("Reason", "Reason", None)
        ]
        
        entries = {}
        
        for i, (key, label, values) in enumerate(form_fields):
            ttk.Label(dialog, text=label).grid(row=i, column=0, sticky='w', padx=10, pady=5)
            
            if values:
                # 콤보박스
                widget = ttk.Combobox(dialog, values=values, state="readonly", width=30)
            elif key == "Purchase Date":
                # 날짜 선택
                widget = DateEntry(dialog, width=27, background='darkblue', foreground='white', borderwidth=2)
            else:
                # 텍스트 입력
                widget = ttk.Entry(dialog, width=30)
            
            widget.grid(row=i, column=1, sticky='w', padx=10, pady=5)
            entries[key] = widget
        
        # 기존 데이터 로드
        if asset_id:
            try:
                asset = self.manager.get_asset(asset_id)
                if asset:
                    for key, widget in entries.items():
                        if key == "Purchase Date":
                            if asset[key]:
                                widget.set_date(asset[key])
                        else:
                            widget.set(asset[key] if asset[key] else "")
            except Exception as e:
                messagebox.showerror("오류", f"자산 데이터를 불러오는 중 오류가 발생했습니다:\n{str(e)}")
                logger.error(f"Error loading asset data: {e}")
        
        # 버튼 프레임
        button_frame = ttk.Frame(dialog)
        button_frame.grid(row=len(form_fields), column=0, columnspan=2, pady=20)
        
        def submit():
            try:
                asset_data = {}
                for key, widget in entries.items():
                    if key == "Purchase Date":
                        asset_data[key] = widget.get_date()
                    else:
                        asset_data[key] = widget.get()
                
                if title == "자산 추가":
                    self.manager.add_asset(asset_data)
                    messagebox.showinfo("완료", "자산이 추가되었습니다.")
                else:
                    self.manager.update_asset(asset_id, asset_data)
                    messagebox.showinfo("완료", "자산이 수정되었습니다.")
                
                self.refresh_treeview()
                dialog.destroy()
                
            except Exception as e:
                messagebox.showerror("오류", f"자산 저장 중 오류가 발생했습니다:\n{str(e)}")
                logger.error(f"Error saving asset: {e}")
        
        submit_button = ttk.Button(button_frame, text="저장", command=submit)
        submit_button.pack(side='left', padx=10)
        
        cancel_button = ttk.Button(button_frame, text="취소", command=dialog.destroy)
        cancel_button.pack(side='left', padx=10)
    
    def export_data(self):
        """데이터를 CSV로 내보냅니다."""
        try:
            from datetime import datetime
            import csv
            
            filename = f"asset_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
            
            with open(filename, 'w', newline='', encoding='utf-8-sig') as csvfile:
                fieldnames = ["ID", "Type", "Model", "Purchase Date", "Warranty", "Status", "Location", "Reason"]
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                
                writer.writeheader()
                assets = self.manager.list_assets()
                for asset_id, asset_data in assets.items():
                    row = {"ID": asset_id, **asset_data}
                    writer.writerow(row)
            
            messagebox.showinfo("내보내기 완료", f"데이터가 {filename} 파일로 내보내졌습니다.")
            
        except Exception as e:
            messagebox.showerror("내보내기 오류", f"데이터 내보내기 중 오류가 발생했습니다:\n{str(e)}")
            logger.error(f"Export error: {e}")
    
    def on_closing(self):
        """애플리케이션 종료 시 처리"""
        try:
            self.manager.close()
        except Exception as e:
            logger.error(f"Error closing manager: {e}")
        self.root.destroy()

def main():
    root = tk.Tk()
    app = ITAssetManagerGUI(root)
    
    # 종료 이벤트 처리
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    
    root.mainloop()

if __name__ == "__main__":
    main()

