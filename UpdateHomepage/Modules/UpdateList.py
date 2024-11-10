import requests
import os

def get_latest_version(url):
    response = requests.get(url)
    response.raise_for_status()  # 确保请求成功
    releases = response.json()
    if releases:
        latest_version = releases[0]['tag_name']  # 获取最新版本号
        return latest_version
    else:
        raise ValueError("无法找到最新版本号")

def update_xaml_file(save_path, new_version):
    # 目标 XAML 文件的路径
    xaml_file_path = os.path.join(save_path, "History.xaml")
    
    # 如果目标文件已经存在，先删除
    if os.path.exists(xaml_file_path):
        os.remove(xaml_file_path)
        print(f"文件 {xaml_file_path} 已存在，已删除旧文件。")
    
    # 读取现有的 XAML 文件内容（或初始化为一个默认模板）
    xaml_content = '''
        <ContentControl Content="历 史 版 本 " Template="{StaticResource Separator}" Margin="0,15,0,0"/>

        <local:MyCard Title="文章存档" Margin="0,5">
            <StackPanel Margin="25,40,23,15">
                <Grid>
                    <Grid.ColumnDefinitions>
                        <ColumnDefinition Width="1*"/>
                        <ColumnDefinition Width="100"/>
                    </Grid.ColumnDefinitions>

                    <local:MyComboBox x:Name="jumpbox" Height="30" SelectedIndex="0">
                        <local:MyComboBoxItem Content="2.8.8"/>
                    </local:MyComboBox>

                    <local:MyButton HorizontalAlignment="Center" Width="80"
                                    Grid.Column="1" Text="打开→" EventType="打开帮助"
                                    EventData="{Binding Path=Text,ElementName=jumpbox,StringFormat=https://updatehomepage.pages.dev/{0}.json}"/>
                </Grid>
            </StackPanel>
        </local:MyCard>'''

    # 检查是否已有新版本，如果没有添加新版本
    if f'<local:MyComboBoxItem Content="{new_version}"/>' not in xaml_content:
        # 替换 ComboBox 中的内容部分，添加新版本项
        xaml_content = xaml_content.replace(
            '<local:MyComboBoxItem Content="2.8.8"/>',
            f'    <local:MyComboBoxItem Content="2.8.8"/>\n    <local:MyComboBoxItem Content="{new_version}"/>'
        )
        # 保存更新后的 XAML 文件
        with open(xaml_file_path, 'w', encoding='utf-8') as file:
            file.write(xaml_content)
        print(f"文件 {xaml_file_path} 已更新，包含新版本 {new_version}")
    else:
        print(f"版本 {new_version} 已经存在，无需更新。")

if __name__ == "__main__":
    url = "https://api.github.com/repos/Hex-Dragon/PCL2/releases"
    save_path = r"H:\UpdateHomepage"  # 保存路径

    # 获取最新版本号
    latest_version = get_latest_version(url)

    # 更新 XAML 文件，添加新版本
    update_xaml_file(save_path, latest_version)
