   M S B A M L   `   `   `  ����L  HInterfaceFrontend, Version=1.0.0.0, Culture=neutral, PublicKeyToken=null5clr-namespace:InterfaceFrontendInterfaceFrontend  5   	   "    InterfaceFrontend.MainWindow   5   	   R NWindowsBase, Version=4.0.0.0, Culture=neutral, PublicKeyToken=31bf3856ad364e35W SPresentationCore, Version=4.0.0.0, Culture=neutral, PublicKeyToken=31bf3856ad364e35\ XPresentationFramework, Version=4.0.0.0, Culture=neutral, PublicKeyToken=31bf3856ad364e35D 9http://schemas.microsoft.com/winfx/2006/xaml/presentation    5   	   R NSystem.Xaml, Version=4.0.0.0, Culture=neutral, PublicKeyToken=b77a5c561934e089:x,http://schemas.microsoft.com/winfx/2006/xaml     5   	   @d2http://schemas.microsoft.com/expression/blend/2008     5   	   Jmc;http://schemas.openxmlformats.org/markup-compatibility/2006     5   	   1localclr-namespace:InterfaceFrontend     5   	   -   5          � Title$  	Interface��5   	    � WindowStyle$ SingleBorderWindow=�5	   	    � AllowsTransparency .  
�������$
��1080��5   	   $
��1920��5   	   .��5      �  � RowDefinitions 5   
   �� 5      $��95 �6   �� 5      $
��460* �6   �� 5      $
��460* �6   �� 5      $	��50* �6    � ColumnDefinitions 5   
   �� 5      $	��120 �6   �� 5      .+�5   
   ��  �� Orientation$ 
Horizontal=�5      $	��Top=�5      $
��auto��5       $��2��5!      $��0��5"      
�������.+�5$      d� -   5         d�Name$ BurgerMenuToggleButton��5%      $��40��5&      $��40��5'      $
��Left=�5(      $	��Top=�5)      $��	10,25,0,0q�5*      .��5,      �� $	��☰��5-      $��16(�5.      $
��Left=�5/      $��Center=�50      52      �� 53      $���{C:\Schule\Diplomarbeit\Repo\ProjectHelios\Intelligence Module\PDF Recoc\InterfaceBackend\InterfaceFrontend\FW_Braunau-1.png��54      $	��Top=�55      $��85��56      $	��800��57      $��0,5,0,5q�58      �� 5:      ${��uC:\Schule\Diplomarbeit\Repo\ProjectHelios\Intelligence Module\PDF Recoc\InterfaceBackend\InterfaceFrontend\HELIOS.png��5;      $��85��5<      $	��800��5=      $��0,5,0,5q�5>      5@      �� 5C   
   -   5         ��Name$ SideMenu��5D      $ Vertical=�5E      $	��120��5F      $��Center=�5G      $��1��5H      $y�	Collapsed=�5I      .+�5K      �� -   5         ��Name$ imageSelectionComboBox��5L      $	��110��5N      $y�Visible=�5O      $��0,5,0,0q�5P      .@�5Q      �� $��Single��6   �� 5R      $��Multi��6   5S      �� 5U      -   5        	 ��Name$	 uploadButton��5V      $��Upload Images��5W      $	��110��5Y      $��0,5,0,0q�5Z      $y�Visible=�5[      �� 5]      -   5        $	 confirmButton��5^      $��Confirm��5_      $	��110��5a      $��0,5,0,0q�5b      $y�	Collapsed=�5c      �� 5e      -   5        $	 
MoveButton��5f      $��Bewegen��5g      $	��110��5i      $��0,5,0,0q�5j      $y�	Collapsed=�5k      �� 5m      -   5        $	 ScaleButton��5n      $��	Skalieren��5o      $	��110��5q      $��0,5,0,0q�5r      $y�	Collapsed=�5s      �� 5u      -	   5        $	 
DrawButton��5v      $��Zeichnen��5w      $	��110��5y      $��0,5,0,0q�5z      $y�	Collapsed=�5{      �� 5}      -
   5        $	 EraseButton��5~      $��Löschen��5      $	��110��5�      $��0,5,0,0q�5�      $y�	Collapsed=�5�      5�      �� 5�   
   -   5        
 ��Name$
 InfoCurrentImageBox��5�      $y�	Collapsed=�5�      
�����@�
���   �$��14(�5�      $��Stretch=�5�      $��2��5�      d� 5�   
   -   5        $ InfoCurrentImage��5�      $y�	Collapsed=�5�      $	��110��5�      $��40��5�      $��3��5�      .��5�   
   �� $
��Info��5�      $��16(�5�      $��Center=�5�      $��Center=�5�      5�      �� 5�   
   -   5         ��Name$ imageCanvas��5�      
�������$��1��5�      $��1��5�      $��3��5�      5�      5�      