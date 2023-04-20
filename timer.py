import tkinter, sys, os, pickle
import pygame

def rgb_to_hex(r: int, g: int, b: int):
    # check if in range 0~255
    assert 0 <= r <= 255
    assert 0 <= g <= 255
    assert 0 <= b <= 255
 
    r = f"{r:x}"
    g = f"{g:x}"
    b = f"{b:x}"
    # re-write '7' to '07'
    r = (2 - len(r)) * '0' + r
    g = (2 - len(g)) * '0' + g
    b = (2 - len(b)) * '0' + b
 
    hex_color = '#' + r + g + b
    return hex_color

class File:
    "저장 및 불러오기 클래스"
    def __init__(self):
        self.__resource_folder: str = os.path.join(os.path.dirname(sys.argv[0]), "Resource")
        self.__filename: str = f"{self.__class__.__name__}.p"
        self.__path: str = os.path.join(self.__resource_folder, self.__filename)

        if os.path.isdir(self.__resource_folder) is False:
            os.mkdir(self.__resource_folder)

    def load(self) -> pickle:
        """return: 정보를 불러옴
        정보가 담긴 파일이 없다면 새로 저장함"""
        if os.path.isfile(self.__path) is False:
            self.save()
            return self

        with open(self.__path, "rb") as f:
            data = pickle.load(f)
        return data

    def save(self):
        "정보를 저장함"
        with open(self.__path, "wb") as f:
            pickle.dump(self, f)

class Setting(File):
    "기본적인 설정이 담겨있는 클래스"
    def __init__(self):
        super().__init__()
        self.run: bool = True
        self.win_SIZE: tuple = (800, 200)
        self.FPS: int = 60
        self.is_width_or_length: bool = True

        self.time: float = 90
        self.fontsize: int = 25
        self.final: float = 5

class Color(File):
    "사용한 색이 담겨있는 클래스"
    def __init__(self):
        super().__init__()
        self.background = [255, 255, 255]
        self.timmer_bar = [184, 184, 184]
        self.timer_num = [0, 0, 0]
        self.timer_num_final = [255, 0, 0]

class Timer:
    "Timmer_Bar & Timer_Num 두 클래스를 동작시키는 클래스"
    def __init__(self, setting, color):
        if setting.is_width_or_length:
            # 가로 가면
            x, y = 10, 100
            width, height = 780, 30
        else: # 세로 라면
            x, y = 100, 10
            width, height = 30, 780
        self.time = setting.time
        self.timmer_bar = Timmer_Bar(setting=setting, color=color, time_max=setting.time, x=x, y=y, width=width, height=height)
        self.timer_num = Timer_Num(setting=setting, color=color)

    def __persent_process(self, CLOCK):
        "시간을 계속 깍는 함수"
        self.time -= CLOCK.get_time() / 1000
    
    def update(self, win, CLOCK):
        "시간을 타이머들에게 넘겨줌"
        self.__persent_process(CLOCK)
        if self.time < 0:
            self.time = 0

        self.timmer_bar.update(win, self.time)
        self.timer_num.update(win, self.time)

class Timmer_Bar:
    "타이머의 바 를 그리는 클래스"
    def __init__(self, setting, color, time_max, x, y, width, height):
        self.setting = setting
        self.x, self.y = x, y
        self.width, self.height = width, height
        self.rect = pygame.rect.Rect(self.x, self.y, self.width, self.height)

        self.time_max = time_max
        self.color = color.timmer_bar

        self.width_or_length_function = self.width_update if setting.is_width_or_length else self.length_update
    
    def update(self, win, time):
        "넘겨받은 시간에 따라 바를 만듦"
        self.width_or_length_function(win, time)
    
    def width_update(self, win, time):
        "가로"
        self.rect.width = (time / self.time_max) * self.width

        self.rect.centery = win.get_rect().centery
        pygame.draw.rect(win, self.color, self.rect)

    def length_update(self, win, time):
        "세로"
        space = (time / self.time_max) * self.height

        self.rect.y = self.y + self.height - space
        self.rect.height = space
        self.rect.centerx = win.get_rect().centerx
        pygame.draw.rect(win, self.color, self.rect)

class Timer_Num:
    "타이머의 숫자를 표시하는 함수"
    def __init__(self, setting, color):
        self.setting = setting
        self.color = color

        self.font = pygame.font.SysFont("Verdana", setting.fontsize)
        self.num_color = color.timer_num

    def update(self, win, time):
        "숫자를 표시 함"
        self.num_color = self.color.timer_num if time > self.setting.final else self.color.timer_num_final

        text = self.font.render(f"{time:.1f}", True, self.num_color)
        text_rect = text.get_rect(center=(self.setting.win_SIZE[0]/2, self.setting.win_SIZE[1]/2))
        win.blit(text, text_rect)

class Window:
    "설정창을 만드는 클래스"
    def __init__(self):
        # 기본 변수
        self.setting = Setting().load()
        self.color = Color().load()

        self.win_size_width = (800, 200)
        self.win_size_length = (200, 800)

        # 윈도우 시작
        self.win = tkinter.Tk()

        self.win.title("타이머")
        self.win.geometry("250x320")

        if os.path.isfile(os.path.join(os.path.dirname(sys.argv[0]), "Resource", icon_file)):
            self.win.iconbitmap(os.path.join(os.path.dirname(sys.argv[0]), "Resource", icon_file))
        self.win.resizable(False, False)

        self.setting_frame()
        self.color_frame()
        self.width_or_length_frame()

        button = tkinter.Button(self.win, text="타이머 시작", command=self.timer_start)
        button.pack()

        self.win.mainloop()

    def setting_frame(self):
        setting_frame = tkinter.LabelFrame(self.win, text="세팅 설정", labelanchor="n")
        setting_frame.pack()

        timer_setting_label = tkinter.Label(setting_frame, text="시간(초)")
        timer_setting_label.grid(row=0, column=0)
        self.time_setting_entry = tkinter.Entry(setting_frame)
        self.time_setting_entry.insert(0, self.setting.time)
        self.time_setting_entry.bind("<Key>", self.event_setting_save)
        self.time_setting_entry.grid(row=0, column=1)

        fontsize_setting_label = tkinter.Label(setting_frame, text="숫자크기")
        fontsize_setting_label.grid(row=1, column=0)
        self.fontsize_setting_entry = tkinter.Entry(setting_frame)
        self.fontsize_setting_entry.insert(0, self.setting.fontsize)
        self.fontsize_setting_entry.bind("<Key>", self.event_setting_save)
        self.fontsize_setting_entry.grid(row=1, column=1)

        final_setting_label = tkinter.Label(setting_frame, text="마지막 초세기")
        final_setting_label.grid(row=2, column=0)
        self.final_setting_entry = tkinter.Entry(setting_frame)
        self.final_setting_entry.insert(0, self.setting.final)
        self.final_setting_entry.bind("<Key>", self.event_setting_save)
        self.final_setting_entry.grid(row=2, column=1)

    def color_frame(self):
        color_frame = tkinter.LabelFrame(self.win, text="색깔 설정", labelanchor="n")
        color_frame.pack()

        tkinter.Label(color_frame, text="R").grid(row=0, column=1)
        tkinter.Label(color_frame, text="G").grid(row=0, column=2)
        tkinter.Label(color_frame, text="B").grid(row=0, column=3)

        background_label = tkinter.Label(color_frame, text="배경")
        background_label.grid(row=1, column=0)
        self.background_R_entry = tkinter.Entry(color_frame, width= 5)
        self.background_R_entry.insert(0, self.color.background[0])
        self.background_R_entry.bind("<Key>", self.event_color_save)
        self.background_R_entry.grid(row=1, column=1)
        self.background_G_entry = tkinter.Entry(color_frame, width= 5)
        self.background_G_entry.insert(0, self.color.background[1])
        self.background_G_entry.bind("<Key>", self.event_color_save)
        self.background_G_entry.grid(row=1, column=2)
        self.background_B_entry = tkinter.Entry(color_frame, width= 5)
        self.background_B_entry.insert(0, self.color.background[2])
        self.background_B_entry.bind("<Key>", self.event_color_save)
        self.background_B_entry.grid(row=1, column=3)
        self.background_canvas = tkinter.Canvas(color_frame, width=20, height=20, background=rgb_to_hex(*self.color.background))
        self.background_canvas.grid(row=1, column=4)

        timmer_bar_label = tkinter.Label(color_frame, text="타이머바 색")
        timmer_bar_label.grid(row=2, column=0)
        self.timmer_bar_R_entry = tkinter.Entry(color_frame, width= 5)
        self.timmer_bar_R_entry.insert(0, self.color.timmer_bar[0])
        self.timmer_bar_R_entry.bind("<Key>", self.event_color_save)
        self.timmer_bar_R_entry.grid(row=2, column=1)
        self.timmer_bar_G_entry = tkinter.Entry(color_frame, width= 5)
        self.timmer_bar_G_entry.insert(0, self.color.timmer_bar[1])
        self.timmer_bar_G_entry.bind("<Key>", self.event_color_save)
        self.timmer_bar_G_entry.grid(row=2, column=2)
        self.timmer_bar_B_entry = tkinter.Entry(color_frame, width= 5)
        self.timmer_bar_B_entry.insert(0, self.color.timmer_bar[2])
        self.timmer_bar_B_entry.bind("<Key>", self.event_color_save)
        self.timmer_bar_B_entry.grid(row=2, column=3)
        self.timmer_bar_canvas = tkinter.Canvas(color_frame, width=20, height=20, background=rgb_to_hex(*self.color.timmer_bar))
        self.timmer_bar_canvas.grid(row=2, column=4)

        timer_num_label = tkinter.Label(color_frame, text="타이머숫자 색")
        timer_num_label.grid(row=3, column=0)
        self.timer_num_R_entry = tkinter.Entry(color_frame, width= 5)
        self.timer_num_R_entry.insert(0, self.color.timer_num[0])
        self.timer_num_R_entry.bind("<Key>", self.event_color_save)
        self.timer_num_R_entry.grid(row=3, column=1)
        self.timer_num_G_entry = tkinter.Entry(color_frame, width= 5)
        self.timer_num_G_entry.insert(0, self.color.timer_num[1])
        self.timer_num_G_entry.bind("<Key>", self.event_color_save)
        self.timer_num_G_entry.grid(row=3, column=2)
        self.timer_num_B_entry = tkinter.Entry(color_frame, width= 5)
        self.timer_num_B_entry.insert(0, self.color.timer_num[2])
        self.timer_num_B_entry.bind("<Key>", self.event_color_save)
        self.timer_num_B_entry.grid(row=3, column=3)
        self.timer_num_canvas = tkinter.Canvas(color_frame, width=20, height=20, background=rgb_to_hex(*self.color.timer_num))
        self.timer_num_canvas.grid(row=3, column=4)

        timer_num_final_label = tkinter.Label(color_frame, text="마지막 숫자색")
        timer_num_final_label.grid(row=4, column=0)
        self.timer_num_final_R_entry = tkinter.Entry(color_frame, width= 5)
        self.timer_num_final_R_entry.insert(0, self.color.timer_num_final[0])
        self.timer_num_final_R_entry.bind("<Key>", self.event_color_save)
        self.timer_num_final_R_entry.grid(row=4, column=1)
        self.timer_num_final_G_entry = tkinter.Entry(color_frame, width= 5)
        self.timer_num_final_G_entry.insert(0, self.color.timer_num_final[1])
        self.timer_num_final_G_entry.bind("<Key>", self.event_color_save)
        self.timer_num_final_G_entry.grid(row=4, column=2)
        self.timer_num_final_B_entry = tkinter.Entry(color_frame, width= 5)
        self.timer_num_final_B_entry.insert(0, self.color.timer_num_final[2])
        self.timer_num_final_B_entry.bind("<Key>", self.event_color_save)
        self.timer_num_final_B_entry.grid(row=4, column=3)
        self.timer_num_final_canvas = tkinter.Canvas(color_frame, width=20, height=20, background=rgb_to_hex(*self.color.timer_num_final))
        self.timer_num_final_canvas.grid(row=4, column=4)
    
    def width_or_length_frame(self):
        """가로 또는 세로 프레임
        가로 True, 세로 False"""
        width_or_length_frame = tkinter.LabelFrame(self.win, text="가로 세로 설정", labelanchor="n")
        width_or_length_frame.pack()

        self.is_radiovalue = tkinter.BooleanVar()
        self.width_radio = tkinter.Radiobutton(width_or_length_frame, text="가로", value=True, variable=self.is_radiovalue, command=self.width_or_length_save)
        self.width_radio.pack()
        self.length_radio = tkinter.Radiobutton(width_or_length_frame, text="세로", value=False, variable=self.is_radiovalue, command=self.width_or_length_save)
        self.length_radio.pack()

        self.radio_choice(self.is_radiovalue).select()
    
    def radio_choice(self, isbool: bool):
        return self.width_radio if self.setting.is_width_or_length else self.length_radio

    def event_setting_save(self, event):
        "버튼 입력등의 이벤트 실행 시 실행, 세팅 저장"

        time = self.time_setting_entry.get()
        fontsize = self.fontsize_setting_entry.get()
        final = self.final_setting_entry.get()

        if (time.isdigit() is True) and (fontsize.isdigit() is True):
            self.setting.time = int(time)
            self.setting.fontsize = int(fontsize)
            self.setting.final = int(final)
            self.setting.save()

    def width_or_length_save(self):
        "가로세로 설정 변경시 마다 실행, 세팅 저장"
        self.setting.is_width_or_length = self.is_radiovalue.get()
        self.setting.win_SIZE = (800, 200) if self.setting.is_width_or_length else (200, 800)
        print(self.setting.win_SIZE)
        self.setting.save()

    def event_color_save(self, event):
        "버튼 입력등의 이벤트 실행 시 실행, RGB 저장"

        background_R = self.background_R_entry.get()
        background_G = self.background_G_entry.get()
        background_B = self.background_B_entry.get()
        timmer_bar_R = self.timmer_bar_R_entry.get()
        timmer_bar_G = self.timmer_bar_G_entry.get()
        timmer_bar_B = self.timmer_bar_B_entry.get()
        timer_num_R = self.timer_num_R_entry.get()
        timer_num_G = self.timer_num_G_entry.get()
        timer_num_B = self.timer_num_B_entry.get()
        timer_num_final_R = self.timer_num_final_R_entry.get()
        timer_num_final_G = self.timer_num_final_G_entry.get()
        timer_num_final_B = self.timer_num_final_B_entry.get()

        if (background_R.isdigit() is True) and (background_G.isdigit() is True) and (background_B.isdigit() is True) and\
            (timmer_bar_R.isdigit() is True) and (timmer_bar_G.isdigit() is True) and (timmer_bar_B.isdigit() is True) and\
            (timer_num_R.isdigit() is True) and (timer_num_G.isdigit() is True) and (timer_num_B.isdigit() is True):
            self.color.background[0] = int(background_R)
            self.color.background[1] = int(background_G)
            self.color.background[2] = int(background_B)
            self.color.timmer_bar[0] = int(timmer_bar_R)
            self.color.timmer_bar[1] = int(timmer_bar_G)
            self.color.timmer_bar[2] = int(timmer_bar_B)
            self.color.timer_num[0] = int(timer_num_R)
            self.color.timer_num[1] = int(timer_num_G)
            self.color.timer_num[2] = int(timer_num_B)
            self.color.timer_num_final[0] = int(timer_num_final_R)
            self.color.timer_num_final[1] = int(timer_num_final_G)
            self.color.timer_num_final[2] = int(timer_num_final_B)

            self.background_canvas.config(background=rgb_to_hex(*self.color.background))
            self.timmer_bar_canvas.config(background=rgb_to_hex(*self.color.timmer_bar))
            self.timer_num_canvas.config(background=rgb_to_hex(*self.color.timer_num))
            self.timer_num_final_canvas.config(background=rgb_to_hex(*self.color.timer_num_final))
            self.color.save()
    
    def timer_start(self):
        self.setting.save()
        self.color.save()
        self.win.destroy()
        timer_start(self.setting, self.color)

def timer_start(setting: Setting, color: Color):
    pygame.init()

    win = pygame.display.set_mode(setting.win_SIZE)
    pygame.display.set_caption(f"{setting.time}s Timer")

    # 기본 설정
    CLOCK = pygame.time.Clock()

    # 타이머 설정
    start = False
    timmer = Timer(setting=setting, color=color)

    while setting.run:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                setting.run = False

            if event.type == pygame.MOUSEBUTTONDOWN or event.type == pygame.KEYDOWN:
                start = True

        # 배경화면 및 타이머바 그리기
        win.fill(color.background)
        if start is True:
            timmer.update(win, CLOCK)

        # 업데이트
        pygame.display.update()
        CLOCK.tick(60)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    icon_file = "nari.ico"
    Window()