#!/usr/bin/env python
#coding=utf-8

# @File: generate_app.py
# @Auther: zhengqingquan
# @Date: 2024/07/18
# @Version: 1.0.0
# @Brief: Based on ASR platform code, it is possible to automatically generate Python scripts for the APP.
# @Instructions: Place the script in the root directory, modify the name of the app you need, and then execute it. And open the corresponding macro control.

import os
import sys
import re
import argparse
import logging

# APP 名称，例如：NewApp
app_name = 'NewApp'

# APP 文件夹名称，例如：newapp
app_file_name = f'{app_name.lower()}'

# APP 配置项的名称，例如：MMI_SUPPORT_NEWAPP
app_configuration_name = f'MMI_SUPPORT_{app_name.upper()}'

# APP 宏控的宏名，例如：CONFIG_MMI_SUPPORT_NEWAPP
app_macro_name = f'CONFIG_MMI_SUPPORT_{app_name.upper()}'

# APP 类名，例如：NewApp
app_class_name = app_name

# 客户端类名，例如：NewAppclient
app_client_class_name = f'{app_name}Client'

# 资源文件名称，例如：NewApp_res
res_h_file_name = f'{app_name}_res'

# APP 文件名称，例如：NewAppAPP
app_h_file_name = f'{app_name}APP'

# 客户端文件名称，例如：NewAppClient
client_h_file_name = f'{app_name}Client'

# 分辨率
resolution = 'asr-480x960'

def insert_text_fun(file_name, pattern, insert_text, position):
    try:
        # 读取文件内容
        with open(file_name, 'r', encoding='utf-8') as file:
            if insert_text in file.read():
                return logging.info(f'Content repetition:{insert_text}')
            lines = file.readlines()

        # 找到匹配的位置
        for i in range(len(lines)):
            line = lines[i].strip()
            if pattern in line:
                lines.insert(i + position, insert_text) # 插入位置在匹配行的下一行

        # 写入文件
        with open(file_name, 'w') as file:
            file.writelines(lines)
    except FileNotFoundError:
        logging.error(f"File {file_name} not exist!")

def add_configuration_items():

    # 需要修改的文件的路径
    file_name = 'evb/src/gui/Kconfig'

    # 定义匹配的正则表达式模式，寻找需要插入的位置。
    pattern = r'^menu "mUI app configurations"$'

    # 定义要插入的文本
    insert_text = f'''
config {app_configuration_name}
	bool "enable {app_name} app"
	default n
	help
	  Select this option if you want to support {app_name}.
'''

    # 读取文件内容
    with open(file_name, 'r') as file:
        lines = file.readlines()

    # 找到匹配的位置
    for i in range(len(lines)):
        line = lines[i].strip()
        if re.match(pattern, line):
            lines.insert(i + 1, insert_text) # 插入位置在匹配行的下一行

    # 写入文件
    with open(file_name, 'w') as file:
        file.writelines(lines)

def modify_cmake_file():
    # 文件名
    file_name = 'evb/src/gui/mgapollo/CMakeLists.txt'

    # 定义要插入的文本
    insert_text = f'''
if (DEFINED CONFIG_MMI_SUPPORT_{app_name.upper()})
    file(GLOB {app_name}_cpp_files   RELATIVE ${{CMAKE_CURRENT_SOURCE_DIR}}
        apps/{app_name}/src/*.cpp
    )
    set (library_cpp_files ${{library_cpp_files}} ${{{app_name}_cpp_files}})
endif()'''

    # 定义匹配的正则表达式模式
    pattern = r'^file\(GLOB library_cpp_files\s+RELATIVE\s+\${CMAKE_CURRENT_SOURCE_DIR}$'
    pattern2 = r'^\)$'

    # 读取文件内容
    with open(file_name, 'r') as file:
        lines = file.readlines()

    # 找到匹配行的位置
    match_indices = []
    is_statr_search_right_bracket = False
    for i in range(len(lines)):
        line = lines[i].strip()
        if re.match(pattern, line):
            is_statr_search_right_bracket = True
        if re.match(pattern2, line) and is_statr_search_right_bracket:
            match_indices.append(i + 1)  # 插入位置在匹配行的下一行
            break

    # 在匹配行的下一行插入文本
    for index in match_indices:
        lines.insert(index, insert_text + '\n')

    # 将修改后的内容写回文件
    with open(file_name, 'w') as file:
        file.writelines(lines)

def modify_rules_cmake_file():
    # 文件名
    file_name = 'evb/src/gui/mgapollo/rules.cmake'

    # 定义要匹配的函数名
    function_name = 'set(apollo_app_dirs'

    # 定义要插入的文本
    insert_text1 = f'''\
if (DEFINED {app_macro_name})
set (apollo_app_dirs
    ${{apollo_app_dirs}}
    {app_name.lower()}
)
endif()

'''
    # 定义要插入的文本
    insert_text2 = f'''\

if (DEFINED {app_macro_name})
list(APPEND mgapollo_head_files
					"${{__G_MG_SIMULATOR_GEN_DIR}}/mgapollo/apps/{app_file_name}/include"
)
endif()
'''

    # 读取文件内容
    with open(file_name, 'r') as file:
        lines = file.readlines()

    # 找到函数的开始和结束位置
    start_index = -1
    end_index = -1
    for i, line in enumerate(lines):
        if function_name in line:
            start_index = i
        if start_index != -1 and ')' in line:
            end_index = i
            break

    if start_index == -1 or end_index == -1:
        print(f"Error: Function '{function_name}' not found in file '{file_name}'")
        return

    # 在函数体的末尾添加所需内容。
    lines.insert(end_index + 2, insert_text1)

    # 写入文件
    with open(file_name, 'w') as file:
        file.writelines(lines)

    # 在文件末尾追加文本
    with open(file_name, 'a') as file:
        file.write(insert_text2)

def add_respkg_id():

    # 文件名
    file_name = 'evb/src/gui/mgapollo/apps/include/appcommoninclue.h'

    # 定义要匹配的函数名
    function_name = 'enum  _RES'

    # 定义要插入的文本
    insert_text1 = f'''\
#ifdef {app_macro_name}
	RES_PKG_{app_name.upper()}_ID,
#endif
'''

    # 读取文件内容
    with open(file_name, 'r') as file:
        lines = file.readlines()

    # 找到函数的开始和结束位置
    start_index = -1
    end_index = -1
    for i, line in enumerate(lines):
        if function_name in line:
            start_index = i
        if start_index != -1 and '//TODO' in line:
            end_index = i
            break

    if start_index == -1 or end_index == -1:
        print(f"Error: Function '{function_name}' not found in file '{file_name}'")
        return

    # 在函数体的末尾添加所需内容。
    lines.insert(end_index, insert_text1)

    # 写入文件
    with open(file_name, 'w') as file:
        file.writelines(lines)

def create_source_file():

    app_res_h=f'''\
#ifndef __NGUX_{app_name.upper()}_RES_H__
#define __NGUX_{app_name.upper()}_RES_H__

#include "sys_res.h"
#include "appwithbar.h"
#include "{app_h_file_name}.h"

#define RESPKGID      RPKG_{app_name}
#define RESID(name)   R_{app_name}_##name

#include "resdefines.head.h"
#include "{app_name}.res.c"
#include "resundefines.h"

#include "resdefines.name.h"
#include "{app_name}.res.c"
#include "resundefines.h"

#undef RESID
#undef RESPKGID

#endif  /* __NGUX_{app_name.upper()}_RES_H__ */
'''

    app_app_h=f'''\
#ifndef __NGUX_{app_name.upper()}_H__
#define __NGUX_{app_name.upper()}_H__

#include "ngux.h"
#include "appwithbar.h"

USE_NGUX_NAMESPACE

DECLARE_APP_FACTORY({app_name})

/**
 * @brief client
 */
enum {{
    {app_name.upper()}_CLIENT_BEGIN = APP_CLIENT_MAX,
    {app_name.upper()}_CLIENT_MAIN,
    {app_name.upper()}_CLIENT_MAX,
}};

/**
 * @brief event
 */
enum {{
    {app_name.upper()}_CMD_BEGIN = APP_CMD_MAX,
    {app_name.upper()}_CMD_ENTER,
    {app_name.upper()}_CMD_MENU,
    {app_name.upper()}_CMD_CLEAR,
    {app_name.upper()}_CMD_SAVE,
    {app_name.upper()}_CMD_BACK,
    {app_name.upper()}_CMD_MAX
}};

/**
 * @brief {app_name} APP Class.
 */
class {app_name} : public AppWithBar
{{
    DECLARE_CONTROLLER_CLIENTS

    public:
        {app_name}();
        ~{app_name}();

    private:
        void onCreate(ContextStream* contextstream, Intent* intent);
}};

#endif /* __NGUX_{app_name.upper()}_H__ */
'''

    app_client_h=f'''\
#ifndef __NGUX_{client_h_file_name.upper()}_H_
#define __NGUX_{client_h_file_name.upper()}_H_

#include "ngux.h"
#include "appwithbar.h"

USE_NGUX_NAMESPACE

class {app_client_class_name} : public AppClient
{{
    DECLARE_VIEWCONTEXT

    public:
        {app_client_class_name}(Controller* owner, NGInt view_id, View *parent, NGParam param1, NGParam param2);
        ~{app_client_class_name}();

    private:
        NGBool onKey(NGInt keyCode, KeyEvent* event);
        NGUInt onControllerCommand(NGUInt cmd_id, NGParam param1, NGParam param2);
        void active();
        void inactive();
}};

#endif /* __NGUX_{client_h_file_name.upper()}_H_ */
'''

    app_res_cpp=f'''\
#include "ngux.h"
#include "{res_h_file_name}.h"

USE_NGUX_NAMESPACE

#define RESPKGID      RPKG_{app_name}
#define RESID(name)   R_{app_name}_##name

#include "resdefines.source.h"
#include "{app_name}.res.c"
#include "resundefines.h"

#include "resdefines.init.h"
#include "{app_name}.res.c"
#include "resundefines.h"

#undef RESID
#undef RESPKGID
'''

    app_app_cpp=f'''\
#include "ngux.h"
#include "{app_h_file_name}.h"
#include "{client_h_file_name}.h"
#include "{res_h_file_name}.h"

{app_class_name}::{app_class_name}() :AppWithBar(true)
{{
    FRRegister_{app_name}_resource();
}}

{app_class_name}::~{app_class_name}()
{{

}}

void {app_class_name}::onCreate(ContextStream* contextStream, Intent* intent)
{{
    AppWithBar::onCreate(contextStream, intent);
    AppWithBar::setFullScreen(false);
    showView({app_name.upper()}_CLIENT_MAIN, 0, 0);
}}

BEGIN_CONTROLLER_CLIENTS({app_class_name})
    CONTROLLER_CLIENT({app_name.upper()}_CLIENT_MAIN, {app_client_class_name})
END_CONTROLLER_CLIENTS_EX(AppWithBar)

BEGIN_DEFINE_APP({app_class_name})
    APP_SET(name, "{app_name.lower()}")
    APP_SET(position, POS_HIDE)
END_DEFINE_APP
'''

    app_client_cpp=f'''\
#include "ngux.h"
#include "{res_h_file_name}.h"
#include "{app_h_file_name}.h"
#include "{client_h_file_name}.h"

USE_NGUX_NAMESPACE

BEGIN_SETVIEW({app_client_class_name})
END_SETVIEW

BEGIN_GETHANDLE({app_client_class_name})
END_GETHANDLE

{app_client_class_name}::{app_client_class_name}(Controller*owner, int view_id, View *parent, NGParam param1, NGParam param2)
    :AppClient(owner, view_id, parent)
{{
    m_baseView = CreateViewFromRes(R_{app_name}_ui_{app_client_class_name.lower()}_main, parent, this , NULL);
}}

{app_client_class_name}::~{app_client_class_name}()
{{

}}

void {app_client_class_name}::active()
{{
    AppClient::active();
}}

void {app_client_class_name}::inactive()
{{
    AppClient::inactive();
}}

bool {app_client_class_name}::onKey(int keyCode, KeyEvent* event)
{{
    return DISPATCH_CONTINUE_MSG;
}}

NGUInt {app_client_class_name}::onControllerCommand(NGUInt cmd_id, NGParam param1, NGParam param2)
{{
    switch (cmd_id)
    {{
        case {app_name.upper()}_CMD_ENTER:
        {{
            break;
        }}
        case {app_name.upper()}_CMD_CLEAR:
        {{
            break;
        }}
        default:
        {{
            break;
        }}
    }}

    return DISPATCH_STOP_MSG;
}}
'''

    app_res_c=f'''\
begin_respkg({app_name}, RES_PKG_{app_name.upper()}_ID)

    //image resource
    begin_image_res()
    end_image_res

    //drawable resource
    begin_dr_res
    end_dr_res

    //drawableset resource
    begin_drset_res
    end_drset_res

    //ui resource
    begin_uis
        begin_ui_res({app_client_class_name.lower()}_main)
            def_name(showtext)

            begin_theme_view(PanelView, R_sys_var_theme_PanelView)
                setRectWH(0, _ngux_phonebar_h, _ngux_screen_w, _ngux_content_h)
                begin_theme_view(TextView, R_sys_var_theme_TextView)
                    map(my(showtext))
                    setRectWH(0, 0, _ngux_screen_w, _ngux_content_h)
                    set(TextAlign, ALIGN_CENTER)
                    set(TextValign, VALIGN_MIDDLE)
                    set(Text, "{app_name}")
                end_view
            end_view

            begin_mode({app_client_class_name}_def)
                setMode(APP_MENUBAR_LEFTTEXT, 0, 0)
                setMode(APP_MENUBAR_MIDDLETEXT,STRID_COMMON_ECL_TEXT_SIMPLEX_SOFTKEY_SELECT_MK,{app_name.upper()}_CMD_ENTER)
                setMode(APP_MENUBAR_RIGHTTEXT, STRID_IDLESHORTCUTS_ECL_QTN_NAM_SOFTKEY_BACK, APP_CMD_EXIT)
            end_mode

            begin_controller_modes
                add_mode({app_client_class_name}_def)
            end_controller_modes({app_client_class_name}_def)
        end_ui_res
    end_uis

end_respkg
'''

    source_file_path = {
        f"evb/src/gui/mgapollo/apps/{app_name.lower()}/include/{res_h_file_name}.h":app_res_h,
        f"evb/src/gui/mgapollo/apps/{app_name.lower()}/include/{app_h_file_name}.h":app_app_h,
        f"evb/src/gui/mgapollo/apps/{app_name.lower()}/include/{client_h_file_name}.h":app_client_h,
        f"evb/src/gui/mgapollo/apps/{app_name.lower()}/src/{res_h_file_name}.cpp":app_res_cpp,
        f"evb/src/gui/mgapollo/apps/{app_name.lower()}/src/{app_h_file_name}.cpp":app_app_cpp,
        f"evb/src/gui/mgapollo/apps/{app_name.lower()}/src/{client_h_file_name}.cpp":app_client_cpp,
        f"evb/src/gui/mgapollo/resdesc/{resolution}/{app_name.lower()}/include/{app_name.lower()}.res.c":app_res_c,
    }

    for file_path, file_content in source_file_path.items():

        # 获取文件夹路径
        folder_path = os.path.dirname(file_path)

        # 创建文件夹（如果不存在）
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)

        # 创建文件
        with open(file_path, 'w') as f:
            f.write(file_content)

def create_inner_res():
    pass

def add_respkg_enum():
    # evb/src/gui/mgapollo/apps/include/appcommoninclue.h
    pass

def add_entry_function():
    # 文件名
    file_name = 'evb/src/gui/mgapollo/apps/src/Apollo.cpp'

    # 定义要插入的文本
    insert_text = f'''\
#ifdef {app_macro_name}
NGBool Entry{app_name} (Intent *intent)
{{
    AppManager::getInstance()->startApp("{app_name.lower()}", intent);
    return true;
}}
#endif
'''

    # 定义匹配的正则表达式模式
    pattern = r'^NGBool EntryBootUp \(Intent \*intent\)$'

    # 读取文件内容
    with open(file_name, 'r') as file:
        lines = file.readlines()

    # 找到匹配行的位置
    match_indices = []
    for i in range(len(lines)):
        line = lines[i].strip()
        if re.match(pattern, line):
            match_indices.append(i)

    # 在匹配行的下一行插入文本
    for index in match_indices:
        lines.insert(index, insert_text + '\n')

    # 将修改后的内容写回文件
    with open(file_name, 'w') as file:
        file.writelines(lines)

def add_entry_function2():

    # 需要修改的文件的路径
    file_name = 'evb/src/gui/mgapollo/apps/include/appcommoninclue.h'

    # 定义匹配的正则表达式模式，寻找需要插入的位置。
    pattern = r'^#undef __APP_ENTRIES__$'

    pattern2 = r'^#undef __APP_APOLLO__$'

    # 定义要插入的文本
    insert_text = f'''\
#ifdef {app_macro_name}
NGBool Entry{app_name}(Intent* intent);
#endif

'''

    # 定义要插入的文本
    insert_text2 = f'''\
#ifdef {app_macro_name}
#include "{app_h_file_name}.h"
#endif

'''

    # 读取文件内容
    with open(file_name, 'r') as file:
        lines = file.readlines()

    # 找到匹配的位置
    for i in range(len(lines)):
        line = lines[i].strip()
        if re.match(pattern, line):
            # BUG 没有break会输出四行。
            lines.insert(i, insert_text) # 插入位置在匹配行的下一行
            break

    # 找到匹配的位置
    for i in range(len(lines)):
        line = lines[i].strip()
        if re.match(pattern2, line):
            # BUG 没有break会输出四行。
            lines.insert(i, insert_text2) # 插入位置在匹配行的下一行
            break

    # 写入文件
    with open(file_name, 'w') as file:
        file.writelines(lines)

def add_mainframe_entry():

    # 需要修改的文件的路径
    file_name = 'evb/src/gui/mgapollo/apps/launcher/src/MainFrame.cpp'

    # 定义要匹配的函数名
    function_name = r'static APP_ITEM_INFO s_main_app_items[]'

    # 定义要插入的文本
    insert_text = f'''\
#ifdef {app_macro_name}
    {{ Entry{app_name},     STRID_APP_CCA_STR_ID_CCA_SETTING_INFO,
        R_sys_img_app_menu_icon_notepad, R_sys_img_app_menu_icon_small_unuse }},
#endif
'''

    # 读取文件内容
    with open(file_name, 'r') as file:
        lines = file.readlines()

    # 找到函数的开始和结束位置
    start_index = -1
    end_index = -1
    for i, line in enumerate(lines):
        if function_name in line:
            start_index = i
        if start_index != -1 and '};' in line:
            end_index = i
            break

    if start_index == -1 or end_index == -1:
        print(f"Error: Function '{function_name}' not found in file '{file_name}'")
        return

    # 在函数体的末尾添加所需内容。
    lines.insert(end_index, insert_text)

    # 写入文件
    with open(file_name, 'w') as file:
        file.writelines(lines)

def add_app_register():
    # 文件名
    file_name = 'evb/src/gui/mgapollo/apps/src/Apollo.cpp'

    # 定义要匹配的函数名
    function_name = 'registerAppFactories'

    # 定义要插入的文本
    insert_text = f'''\
#ifdef {app_macro_name}
    REGISTER_APP("{app_name.lower()}", {app_class_name});
#endif
'''

    # 读取文件内容
    with open(file_name, 'r') as file:
        lines = file.readlines()

    # 找到函数的开始和结束位置
    start_index = -1
    end_index = -1
    for i, line in enumerate(lines):
        if function_name in line:
            start_index = i
        if start_index != -1 and '}' in line:
            end_index = i
            break

    if start_index == -1 or end_index == -1:
        print(f"Error: Function '{function_name}' not found in file '{file_name}'")
        return

    # 在函数体的末尾添加所需内容。
    lines.insert(end_index, insert_text)

    # 写入文件
    with open(file_name, 'w') as file:
        file.writelines(lines)

def arg_parse():
    # Create parameter parser.
    parser = argparse.ArgumentParser(description='This script is used to generate an ASR platform app.')

    # Add positional arguments
    parser.add_argument('app_name', help='Name of the app to be created, for example: NewAPP.')
    parser.add_argument('resolution', help='The resolution of the device, for example: asr-128x160 or asr-128x64-FWP.')

    # Add otions arguments
    parser.add_argument('-v','--version', help='show version',action='version',version='1.0.0')

    # Check if there are no arguments
    if len(sys.argv) <= 1:
        parser.print_help()
        sys.exit(1)

    # arguments
    args = parser.parse_args()

    # print log
    for key,volue in vars(args).items():
        logging.info(f'{key}:{volue}')

    global app_name
    app_name = args.app_name
    global resolution
    resolution = args.resolution

def start_log():
    # Set the log level to DEBUG to record logs of all levels
    logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

if __name__ == "__main__":

    # TODO 优化代码减小冗余。
    # TODO 优化代码，如果需要添加的内容已经存在，则不添加。防止重复调用的时候，重复添加字符串。

    # 启动日志
    start_log()

    # 处理参数
    # arg_parse()

    # 需要修改的文件的路径
    file_name = 'evb/src/gui/Kconfig'

    # 定义匹配的正则表达式模式，寻找需要插入的位置。
    pattern = r'menu "mUI app configurations"'

    # 定义要插入的文本
    insert_text = f'''
config {app_configuration_name}
	bool "enable {app_name} app"
	default n
	help
	  Select this option if you want to support {app_name}.
'''
    insert_text_fun(file_name, pattern, insert_text, 1)

    # # 增加配置项
    # add_configuration_items()

    # # 添加源文件参与编译。
    # modify_cmake_file()

    # # 添加头文件引用。
    # modify_rules_cmake_file()

    # # 添加资源包ID
    # add_respkg_id()

    # # 添加源文件
    # create_source_file()

    # # 添加内部资源
    # create_inner_res()

    # # 添加APP的入口。
    # add_entry_function()
    # add_entry_function2()

    # # 主菜单添加APP 。
    # add_mainframe_entry()

    # # 注册APP。
    # add_app_register()
