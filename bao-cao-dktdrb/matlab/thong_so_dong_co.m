% THONG_SO_DONG_CO.M - Dong co 1: 700 W | Dong co 2: 1400 W (U = 220 V DC)
clear; clc;
U = 220;  rpm2rad = 2*pi/60;          % dien ap nguon (V); doi vong/phut -> rad/s
% --- DONG CO 1 (700 W, 2050 vong/phut) ---
P1 = 700;   wn1 = 2050*rpm2rad;       % cong suat (W); toc do dinh muc (rad/s)
L1 = 0.02;  R1 = 4.0;                 % dien cam (H); dien tro phan ung (Ohm)
J1 = 0.005; B1 = 0.0005;              % quan tinh (kg.m^2); ma sat nhot (N.m.s/rad)
kPhi1 = 0.96;                         % hang so mo-men / EMF (N.m/A)
Tn1 = P1/wn1;                         % mo-men dinh muc = 3.26 N.m
In1 = (Tn1 + B1*wn1)/kPhi1;           % dong dinh muc = 3.51 A
Imax1 = 2.5*In1;                      % gioi han dong = 8.77 A
% --- DONG CO 2 (1400 W, 2550 vong/phut) ---
P2 = 1400;  wn2 = 2550*rpm2rad;       % cong suat (W); toc do dinh muc (rad/s)
L2 = 0.01;  R2 = 2.0;                 % dien cam (H); dien tro phan ung (Ohm)
J2 = 0.01;  B2 = 0.001;               % quan tinh (kg.m^2); ma sat nhot (N.m.s/rad)
kPhi2 = 0.77;                         % hang so mo-men / EMF (N.m/A)
Tn2 = P2/wn2;                         % mo-men dinh muc = 5.24 N.m
In2 = (Tn2 + B2*wn2)/kPhi2;           % dong dinh muc = 7.16 A
Imax2 = 2.5*In2;                      % gioi han dong = 17.89 A
% --- BO DIEU KHIEN ---
wci = 800; wcw = 60; bw = 0.5;        % bang thong vong dong / vong toc do
Kpi1 = L1*wci; Kii1 = R1*wci;         % PI dong DC1 (dung tham so): 16 ; 3200
Kpi2 = L2*wci; Kii2 = R2*wci;         % PI dong DC2 (dung tham so): 8 ; 1600
KpiG = 1;  KiiG = 100;                % PI dong KHONG dung tham so (ca 2 dong co)
Kpw1 = J1*wcw/kPhi1; Kiw1 = Kpw1*wcw/4;  % PI toc do DC1: 0.3125 ; 4.69
Kpw2 = J2*wcw/kPhi2; Kiw2 = Kpw2*wcw/4;  % PI toc do DC2: 0.779 ; 11.69
KpV = 2;  KiV = 20;                   % PI toc do -> dien ap (khong vong dong)
Kth = 15;                             % P vi tri (1/s)
a1 = 0.6*kPhi1*Imax1/J1; a2 = 0.6*kPhi2*Imax2/J2;  % gia toc ham (gioi han can bac 2)
KpP = 60; KiP = 20; KdP = 4;          % PID vi tri truc tiep -> dien ap
Kc1 = J1*wcw/kPhi1; Kc2 = J2*wcw/kPhi2;  % he so bu cheo dong toc
disp('Da tai thong so: DC1 = 700 W, DC2 = 1400 W');
