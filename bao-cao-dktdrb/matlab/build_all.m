% BUILD_ALL.M
% Tu dong dung cac mo hinh Simulink cho bao cao DKTD cho Robot (DC1 = 700 W, DC2 = 1400 W),
% chay mo phong va ve ket qua cho cac muc I, II.1, II.2, II.3, III.1, III.2.
% Cach dung: dat thong_so_dong_co.m va file nay cung thu muc, mo MATLAB (R2021a tro len) va go:
%     build_all
% Cac mo hinh .slx duoc luu lai trong thu muc hien hanh de mo ra xem / chup anh so do.
clear; clc; close all;
run('thong_so_dong_co.m');
Ts_end = struct();

%% ================= I. HO MACH VONG: Va = 220 V, tai dinh muc =================
mdl = 'M1_OpenLoop_700_1400';
new_model(mdl);
for k = 1:2
    id = num2str(k);  y0 = (k-1)*400;
    add_motor(mdl, id, id, 300, y0);
    blk(mdl, 'simulink/Sources/Step', ['Va' id], [150 60 180 90]+[0 y0 0 y0], 'Time','0','Before','0','After','U');
    blk(mdl, 'simulink/Sources/Constant', ['TL' id], [150 160 180 190]+[0 y0 0 y0], 'Value', ['Tn' id]);
    ln(mdl, ['Va' id '/1'], ['Sum_e' id '/1']);
    ln(mdl, ['TL' id '/1'], ['Sum_T' id '/3']);
    add_logger(mdl, id, ['Va' id '/1'], 1100, y0);
end
save_system(mdl);
set_param(mdl,'StopTime','1');  o = sim(mdl);
plot_scope(o.y1, 'Dong co 1 (700 W): Va = 220 V, tai dinh muc');
plot_scope(o.y2, 'Dong co 2 (1400 W): Va = 220 V, tai dinh muc');
plot_compare({o.y1, o.y2}, {'DC1','DC2'}, 'So sanh 2 dong co, Va = 220 V');

%% ================= II.1 VONG DIEU KHIEN DONG DIEN =================
% i* : 0 -> In (0.02 s) -> 2In (0.07 s) -> 0.5In (0.12 s); tai Tn; (a) PI dung tham so + bu E, (b) PI chung
for k = 1:2
    id = num2str(k);
    In = eval(['In' id]);
    iref = [0 0; 0.02 0; 0.02 In; 0.07 In; 0.07 2*In; 0.12 2*In; 0.12 0.5*In; 0.2 0.5*In];
    assignin('base', ['iref' id], iref);
    for v = 1:2
        mdl = sprintf('M2_Current_DC%s_%s', id, char('a'+v-1));
        new_model(mdl);
        add_motor(mdl, id, id, 500, 0);
        blk(mdl, 'simulink/Sources/From Workspace', 'Iref', [20 60 80 90], 'VariableName', ['iref' id]);
        blk(mdl, 'simulink/Math Operations/Sum', 'SumI', [130 65 150 85], 'Inputs', '+-');
        if v == 1
            P = ['Kpi' id]; I = ['Kii' id];
        else
            P = 'KpiG'; I = 'KiiG';
        end
        blk(mdl, 'simulink/Continuous/PID Controller', 'PI_i', [190 55 260 95], 'Controller','PI','P',P,'I',I, ...
            'LimitOutput','on','UpperSaturationLimit','U','LowerSaturationLimit','-U', ...
            'AntiWindupMode','back-calculation','Kb',[I '/' P]);
        blk(mdl, 'simulink/Math Operations/Sum', 'SumFF', [300 65 320 85], 'Inputs', '++');
        blk(mdl, 'simulink/Discontinuities/Saturation', 'SatU', [360 60 390 90], 'UpperLimit','U','LowerLimit','-U');
        blk(mdl, 'simulink/Math Operations/Gain', 'G_FF', [300 140 340 170], 'Gain', ['kPhi' id], 'Orientation','left');
        blk(mdl, 'simulink/Sources/Constant', 'TL', [380 160 410 190], 'Value', ['Tn' id]);
        ln(mdl,'Iref/1','SumI/1'); ln(mdl,'SumI/1','PI_i/1'); ln(mdl,'PI_i/1','SumFF/1');
        ln(mdl,'SumFF/1','SatU/1'); ln(mdl,'SatU/1',['Sum_e' id '/1']);
        ln(mdl,['Int_i' id '/1'],'SumI/2'); ln(mdl,'TL/1',['Sum_T' id '/3']);
        if v == 1
            ln(mdl,['Int_w' id '/1'],'G_FF/1'); ln(mdl,'G_FF/1','SumFF/2');   % bu suc dien dong
        else
            blk(mdl, 'simulink/Sources/Constant', 'Zero', [240 120 260 140], 'Value','0');
            ln(mdl,'Zero/1','SumFF/2');
        end
        add_logger(mdl, id, 'SatU/1', 1300, 0);
        blk(mdl, 'simulink/Sinks/To Workspace', 'ToWSr', [140 0 200 20], 'VariableName','iref_log','SaveFormat','Timeseries');
        ln(mdl,'Iref/1','ToWSr/1');
        save_system(mdl);
        set_param(mdl,'StopTime','0.17');  o = sim(mdl);
        R.cur{k,v} = o;
    end
    figure('Color','w','Name',['Vong dong DC' id]);
    a = R.cur{k,1}; b = R.cur{k,2};
    plot(a.iref_log.Time, squeeze(a.iref_log.Data),'k--', a.(['y' id]).Time, a.(['y' id]).Data(:,3),'b', ...
         b.(['y' id]).Time, b.(['y' id]).Data(:,3),'r','LineWidth',1.5); grid on;
    legend('i*','PI dung tham so DC','PI khong dung tham so'); xlabel('t (s)'); ylabel('ia (A)');
    title(['Dong co ' id ': dap ung vong dong dien']);
end

%% ================= II.2 VONG DIEU KHIEN TOC DO =================
wref = [200 250];
for k = 1:2
    id = num2str(k);
    assignin('base','wset', wref(k));
    for withI = [1 0]
        mdl = sprintf('M3_Speed_DC%s_%s', id, ternary(withI,'cascade','noI'));
        new_model(mdl);
        add_motor(mdl, id, id, 600, 0);
        blk(mdl, 'simulink/Sources/Step', 'Wref', [20 60 50 90], 'Time','0.1','Before','0','After','wset');
        if withI
            add_cascade(mdl, id, 'Wref/1', 100, 0, false, id, 'bw');
        else
            blk(mdl, 'simulink/Continuous/PID Controller (2DOF)', 'PI_w', [120 50 190 110], 'Controller','PI', ...
                'P','KpV','I','KiV','b','bw','LimitOutput','on','UpperSaturationLimit','U','LowerSaturationLimit','-U', ...
                'AntiWindupMode','back-calculation','Kb','KiV/KpV');
            ln(mdl,'Wref/1','PI_w/1'); ln(mdl,['Int_w' id '/1'],'PI_w/2'); ln(mdl,'PI_w/1',['Sum_e' id '/1']);
        end
        blk(mdl, 'simulink/Sources/Step', 'TL', [480 160 510 190], 'Time','1','Before','0','After',['Tn' id]);
        ln(mdl,'TL/1',['Sum_T' id '/3']);
        add_logger(mdl, id, ternary(withI, ['PI_i' id '/1'], 'PI_w/1'), 1400, 0);
        save_system(mdl);
        set_param(mdl,'StopTime','1.6');  o = sim(mdl);
        plot_scope(o.(['y' id]), sprintf('DC%s: dieu khien toc do %s', id, ternary(withI,'co vong dong','khong vong dong')));
    end
end

%% ================= II.3 VONG DIEU KHIEN VI TRI =================
modes = {'full','speed','direct'};
for k = 1:2
    id = num2str(k);
    ys = {};
    for m = 1:3
        mdl = sprintf('M4_Pos_DC%s_%s', id, modes{m});
        new_model(mdl);
        add_motor(mdl, id, id, 900, 0);
        blk(mdl, 'simulink/Sources/Step', 'Thref', [20 60 50 90], 'Time','0.1','Before','0','After','50');
        blk(mdl, 'simulink/Math Operations/Sum', 'SumTh', [80 65 100 85], 'Inputs','+-');
        ln(mdl,'Thref/1','SumTh/1'); ln(mdl,['Int_th' id '/1'],'SumTh/2');
        switch modes{m}
            case 'full'
                add_posP(mdl, id, id, 'SumTh/1', 130, 0);
                add_cascade(mdl, id, ['PosOut' id '/1'], 450, 0, false);
                vsrc = ['PI_i' id '/1'];
            case 'speed'
                add_posP(mdl, id, id, 'SumTh/1', 130, 0);
                blk(mdl, 'simulink/Continuous/PID Controller (2DOF)', 'PI_w', [470 50 540 110], 'Controller','PI', ...
                    'P','KpV','I','KiV','b','1','LimitOutput','on','UpperSaturationLimit','U','LowerSaturationLimit','-U', ...
                    'AntiWindupMode','back-calculation','Kb','KiV/KpV');
                ln(mdl,['PosOut' id '/1'],'PI_w/1'); ln(mdl,['Int_w' id '/1'],'PI_w/2'); ln(mdl,'PI_w/1',['Sum_e' id '/1']);
                vsrc = 'PI_w/1';
            case 'direct'
                blk(mdl, 'simulink/Continuous/PID Controller', 'PID_th', [140 55 210 95], 'Controller','PID', ...
                    'P','KpP','I','KiP','D','KdP','N','100','LimitOutput','on','UpperSaturationLimit','U', ...
                    'LowerSaturationLimit','-U','AntiWindupMode','back-calculation','Kb','1');
                ln(mdl,'SumTh/1','PID_th/1'); ln(mdl,'PID_th/1',['Sum_e' id '/1']);
                vsrc = 'PID_th/1';
        end
        blk(mdl, 'simulink/Sources/Step', 'TL', [780 160 810 190], 'Time','1','Before','0','After',['0.5*Tn' id]);
        ln(mdl,'TL/1',['Sum_T' id '/3']);
        add_logger(mdl, id, vsrc, 1700, 0);
        save_system(mdl);
        set_param(mdl,'StopTime','1.5');  o = sim(mdl);
        ys{m} = o.(['y' id]); %#ok<SAGROW>
    end
    plot_compare(ys, {'vi tri + toc do + dong','vi tri + toc do','PID truc tiep'}, ['DC' id ': dieu khien vi tri 50 rad'], 1);
end

%% ================= III.1 DONG TOC 2 DONG CO =================
tp = [0 0.1 0.4 2.0 2.3 2.6];  wp = [0 0 150 150 0 0];
assignin('base','wprof',[tp(:) wp(:)]);
mdl = 'M5_SyncSpeed';
new_model(mdl);
blk(mdl, 'simulink/Sources/From Workspace', 'Wprof', [20 260 80 290], 'VariableName','wprof');
for k = 1:2
    id = num2str(k);  y0 = (k-1)*400;
    add_motor(mdl, id, id, 700, y0);
end
% DC1 bam w*; DC2: w2* = (1-ms)*w* + ms*w1   (ms = 0: song song, ms = 1: chu - to)
blk(mdl, 'simulink/Math Operations/Gain', 'Gpar', [120 420 160 450], 'Gain','1-ms');
blk(mdl, 'simulink/Math Operations/Gain', 'Gms',  [120 480 160 510], 'Gain','ms');
blk(mdl, 'simulink/Math Operations/Sum', 'SumR2', [190 440 210 460], 'Inputs','++');
ln(mdl,'Wprof/1','Gpar/1'); ln(mdl,'Gpar/1','SumR2/1'); ln(mdl,'Gms/1','SumR2/2');
add_cascade(mdl, '1', 'Wprof/1', 240, 0, true);
add_cascade(mdl, '2', 'SumR2/1', 240, 400, true);
ln(mdl,'Int_w1/1','Gms/1');
% bu cheo: Delta i1* = -xc*Kc1*(w1-w2), Delta i2* = +xc*Kc2*(w1-w2)
blk(mdl, 'simulink/Math Operations/Sum', 'SumE', [1200 330 1220 350], 'Inputs','+-');
blk(mdl, 'simulink/Math Operations/Gain', 'Gc1', [1260 300 1300 330], 'Gain','-xc*Kc1');
blk(mdl, 'simulink/Math Operations/Gain', 'Gc2', [1260 360 1300 390], 'Gain','xc*Kc2');
ln(mdl,'Int_w1/1','SumE/1'); ln(mdl,'Int_w2/1','SumE/2');
ln(mdl,'SumE/1','Gc1/1'); ln(mdl,'SumE/1','Gc2/1');
ln(mdl,'Gc1/1','SumI1/3'); ln(mdl,'Gc2/1','SumI2/3');
blk(mdl, 'simulink/Sources/Step', 'TL1', [580 160 610 190], 'Time','1.5','Before','0','After','Tn1');
blk(mdl, 'simulink/Sources/Step', 'TL2', [580 560 610 590], 'Time','1.0','Before','0','After','Tn2');
ln(mdl,'TL1/1','Sum_T1/3'); ln(mdl,'TL2/1','Sum_T2/3');
add_logger(mdl, '1', 'PI_i1/1', 1500, 0);  add_logger(mdl, '2', 'PI_i2/1', 1500, 400);
save_system(mdl);
set_param(mdl,'StopTime','2.6');
names = {'Song song','Chu - to','Song song + bu cheo'};  cfg = [0 0; 1 0; 0 1];
figure('Color','w','Name','Dong toc');
for s = 1:3
    assignin('base','ms',cfg(s,1)); assignin('base','xc',cfg(s,2));
    o = sim(mdl);
    t = o.y1.Time; w1 = o.y1.Data(:,2); w2 = interp1(o.y2.Time, o.y2.Data(:,2), t);
    subplot(2,3,s); plot(t,w1,'b',t,w2,'r','LineWidth',1.4); grid on; title(names{s}); legend('\omega_1','\omega_2');
    subplot(2,3,3+s); plot(t,w1-w2,'m','LineWidth',1.4); grid on; title('\omega_1 - \omega_2'); xlabel('t (s)');
    fprintf('%-22s: max|w1-w2| = %.3f rad/s\n', names{s}, max(abs(w1-w2)));
end

%% ================= III.2 VI TRI DONG THOI NHIEU DONG CO =================
tgt = [30 60 -20];  pid = {'1','2','1'};   % truc 3 dung dong co loai 1
tt = (0:1e-3:2.6)';
for useTraj = [0 1]
    for a = 1:3
        [p, v] = traj(tt, tgt(a), useTraj);
        assignin('base', sprintf('thr%d',a), [tt p]);
        assignin('base', sprintf('wff%d',a), [tt v]);
    end
    mdl = sprintf('M6_MultiAxis_%s', ternary(useTraj,'traj','step'));
    new_model(mdl);
    for a = 1:3
        id = num2str(a);  y0 = (a-1)*400;
        add_motor(mdl, id, pid{a}, 1000, y0);
        blk(mdl, 'simulink/Sources/From Workspace', ['Thr' id], [20 60 80 90]+[0 y0 0 y0], 'VariableName',['thr' id]);
        blk(mdl, 'simulink/Sources/From Workspace', ['Wff' id], [20 140 80 170]+[0 y0 0 y0], 'VariableName',['wff' id]);
        blk(mdl, 'simulink/Math Operations/Sum', ['SumTh' id], [100 65 120 85]+[0 y0 0 y0], 'Inputs','+-');
        ln(mdl,['Thr' id '/1'],['SumTh' id '/1']); ln(mdl,['Int_th' id '/1'],['SumTh' id '/2']);
        add_posP(mdl, id, pid{a}, ['SumTh' id '/1'], 140, y0);
        blk(mdl, 'simulink/Math Operations/Sum', ['SumFFw' id], [460 65 480 85]+[0 y0 0 y0], 'Inputs','++');
        blk(mdl, 'simulink/Discontinuities/Saturation', ['SatW' id], [500 60 530 90]+[0 y0 0 y0], ...
            'UpperLimit',['wn' pid{a}],'LowerLimit',['-wn' pid{a}]);
        ln(mdl,['PosOut' id '/1'],['SumFFw' id '/1']); ln(mdl,['Wff' id '/1'],['SumFFw' id '/2']);
        ln(mdl,['SumFFw' id '/1'],['SatW' id '/1']);
        add_cascade(mdl, id, ['SatW' id '/1'], 560, y0, false, pid{a});
        blk(mdl, 'simulink/Sources/Step', ['TL' id], [900 160 930 190]+[0 y0 0 y0], 'Time','1.2','Before','0','After',['0.5*Tn' pid{a}]);
        ln(mdl,['TL' id '/1'],['Sum_T' id '/3']);
        add_logger(mdl, id, ['PI_i' id '/1'], 1800, y0);
    end
    save_system(mdl);
    set_param(mdl,'StopTime','2.6');  o = sim(mdl);
    figure('Color','w','Name',mdl);
    for a = 1:3
        y = o.(sprintf('y%d',a));
        subplot(2,1,1); hold on; plot(y.Time, y.Data(:,1),'LineWidth',1.4);
        subplot(2,1,2); hold on; plot(y.Time, y.Data(:,1)/tgt(a),'LineWidth',1.4);
    end
    subplot(2,1,1); grid on; ylabel('\theta (rad)'); legend('Truc 1','Truc 2','Truc 3'); title(mdl,'Interpreter','none');
    subplot(2,1,2); grid on; ylabel('\theta/\theta_{dich}'); xlabel('t (s)');
end
disp('Hoan thanh tat ca mo phong.');

%% ============================ HAM PHU ============================
function new_model(mdl)
    if bdIsLoaded(mdl), close_system(mdl,0); end
    if exist([mdl '.slx'],'file'), delete([mdl '.slx']); end
    new_system(mdl); open_system(mdl);
    set_param(mdl,'Solver','ode45','MaxStep','1e-4','RelTol','1e-6', ...
        'SaveOutput','off','ReturnWorkspaceOutputs','on');
end

function blk(mdl, lib, name, pos, varargin)
    add_block(lib, [mdl '/' name], 'Position', pos, varargin{:});
end

function ln(mdl, a, b)
    add_line(mdl, a, b, 'autorouting', 'on');
end

function out = ternary(c, a, b)
    if c, out = a; else, out = b; end
end

function add_motor(mdl, id, p, x0, y0)
% Mo hinh DC theo phuong trinh: L di/dt = Va - R i - kPhi w ; J dw/dt = kPhi i - B w - TL ; dth/dt = w
% id: hau to ten khoi ; p: hau to tham so (1 = DC 700 W, 2 = DC 1400 W)
    G = 'simulink/Math Operations/Gain'; S = 'simulink/Math Operations/Sum'; IN = 'simulink/Continuous/Integrator';
    o = [x0 y0 x0 y0];
    blk(mdl, S , ['Sum_e' id] , [0 70 30 100]+o, 'Inputs','+--');
    blk(mdl, G , ['L_inv' id] , [60 70 100 100]+o, 'Gain',['1/L' p]);
    blk(mdl, IN, ['Int_i' id] , [130 70 160 100]+o);
    blk(mdl, G , ['G_R' id]   , [70 130 110 160]+o, 'Gain',['R' p],'Orientation','left');
    blk(mdl, G , ['G_E' id]   , [70 190 110 220]+o, 'Gain',['kPhi' p],'Orientation','left');
    blk(mdl, G , ['G_Te' id]  , [200 70 240 100]+o, 'Gain',['kPhi' p]);
    blk(mdl, S , ['Sum_T' id] , [280 70 310 100]+o, 'Inputs','+--');
    blk(mdl, G , ['J_inv' id] , [340 70 380 100]+o, 'Gain',['1/J' p]);
    blk(mdl, IN, ['Int_w' id] , [420 70 450 100]+o);
    blk(mdl, IN, ['Int_th' id], [500 70 530 100]+o);
    blk(mdl, G , ['G_B' id]   , [350 130 390 160]+o, 'Gain',['B' p],'Orientation','left');
    ln(mdl,['Sum_e' id '/1'],['L_inv' id '/1']); ln(mdl,['L_inv' id '/1'],['Int_i' id '/1']);
    ln(mdl,['Int_i' id '/1'],['G_R' id '/1']);   ln(mdl,['G_R' id '/1'],['Sum_e' id '/2']);
    ln(mdl,['Int_w' id '/1'],['G_E' id '/1']);   ln(mdl,['G_E' id '/1'],['Sum_e' id '/3']);
    ln(mdl,['Int_i' id '/1'],['G_Te' id '/1']);  ln(mdl,['G_Te' id '/1'],['Sum_T' id '/1']);
    ln(mdl,['Int_w' id '/1'],['G_B' id '/1']);   ln(mdl,['G_B' id '/1'],['Sum_T' id '/2']);
    ln(mdl,['Sum_T' id '/1'],['J_inv' id '/1']); ln(mdl,['J_inv' id '/1'],['Int_w' id '/1']);
    ln(mdl,['Int_w' id '/1'],['Int_th' id '/1']);
end

function add_logger(mdl, id, vsrc, x0, y0)
% ghi [theta w ia va] ra workspace (bien y<id>) + Scope
    blk(mdl, 'simulink/Signal Routing/Mux', ['Mux' id], [x0 60 x0+5 140]+[0 y0 0 y0], 'Inputs','4');
    blk(mdl, 'simulink/Sinks/To Workspace', ['ToWS' id], [x0+60 80 x0+120 100]+[0 y0 0 y0], ...
        'VariableName',['y' id],'SaveFormat','Timeseries');
    blk(mdl, 'simulink/Sinks/Scope', ['Scope' id], [x0+60 130 x0+90 160]+[0 y0 0 y0], 'NumInputPorts','3');
    ln(mdl,['Int_th' id '/1'],['Mux' id '/1']); ln(mdl,['Int_w' id '/1'],['Mux' id '/2']);
    ln(mdl,['Int_i' id '/1'],['Mux' id '/3']);  ln(mdl, vsrc, ['Mux' id '/4']);
    ln(mdl,['Mux' id '/1'],['ToWS' id '/1']);
    ln(mdl,['Int_th' id '/1'],['Scope' id '/1']); ln(mdl,['Int_w' id '/1'],['Scope' id '/2']);
    ln(mdl,['Int_i' id '/1'],['Scope' id '/3']);
end

function add_cascade(mdl, id, refSrc, x0, y0, withDelta, p, bstr)
% PI toc do (2DOF, gioi han Imax) -> Sum dong (+ - [+Delta]) -> PI dong (gioi han U) -> Va
    if nargin < 7 || isempty(p), p = id; end
    if nargin < 8, bstr = '1'; end   % trong so setpoint khau P (II.2 dung bw = 0.5)
    o = [x0 y0 x0 y0];
    blk(mdl, 'simulink/Continuous/PID Controller (2DOF)', ['PI_w' id], [0 50 70 110]+o, 'Controller','PI', ...
        'P',['Kpw' p],'I',['Kiw' p],'b',bstr,'LimitOutput','on','UpperSaturationLimit',['Imax' p], ...
        'LowerSaturationLimit',['-Imax' p],'AntiWindupMode','back-calculation','Kb',['Kiw' p '/Kpw' p]);
    blk(mdl, 'simulink/Math Operations/Sum', ['SumI' id], [110 65 130 85]+o, 'Inputs','+-+');
    blk(mdl, 'simulink/Continuous/PID Controller', ['PI_i' id], [170 55 240 95]+o, 'Controller','PI', ...
        'P',['Kpi' p],'I',['Kii' p],'LimitOutput','on','UpperSaturationLimit','U','LowerSaturationLimit','-U', ...
        'AntiWindupMode','back-calculation','Kb',['Kii' p '/Kpi' p]);
    ln(mdl, refSrc, ['PI_w' id '/1']); ln(mdl,['Int_w' id '/1'],['PI_w' id '/2']);
    ln(mdl,['PI_w' id '/1'],['SumI' id '/1']); ln(mdl,['Int_i' id '/1'],['SumI' id '/2']);
    ln(mdl,['SumI' id '/1'],['PI_i' id '/1']); ln(mdl,['PI_i' id '/1'],['Sum_e' id '/1']);
    if ~withDelta
        blk(mdl, 'simulink/Sources/Constant', ['Zero' id], [80 120 100 140]+o, 'Value','0');
        ln(mdl,['Zero' id '/1'],['SumI' id '/3']);
    end
end

function add_posP(mdl, id, p, eSrc, x0, y0)
% w* = sign(e)*min(Kth*|e|, sqrt(2*a*|e|), wn)   (P vi tri co gioi han can bac hai)
    o = [x0 y0 x0 y0];
    blk(mdl, 'simulink/Math Operations/Abs', ['AbsE' id], [0 100 30 130]+o);
    blk(mdl, 'simulink/Math Operations/Gain', ['GKth' id], [60 70 100 100]+o, 'Gain','Kth');
    blk(mdl, 'simulink/Math Operations/Gain', ['G2a' id], [60 130 100 160]+o, 'Gain',['2*a' p]);
    blk(mdl, 'simulink/Math Operations/Sqrt', ['Sqrt' id], [120 130 150 160]+o);
    blk(mdl, 'simulink/Math Operations/MinMax', ['Min' id], [180 90 210 140]+o, 'Function','min','Inputs','2');
    blk(mdl, 'simulink/Discontinuities/Saturation', ['SatWn' id], [230 100 260 130]+o, 'UpperLimit',['wn' p],'LowerLimit','0');
    blk(mdl, 'simulink/Math Operations/Sign', ['SgnE' id], [230 30 260 60]+o);
    blk(mdl, 'simulink/Math Operations/Product', ['PosOut' id], [290 60 320 110]+o);
    ln(mdl, eSrc, ['AbsE' id '/1']); ln(mdl, eSrc, ['SgnE' id '/1']);
    ln(mdl,['AbsE' id '/1'],['GKth' id '/1']); ln(mdl,['AbsE' id '/1'],['G2a' id '/1']);
    ln(mdl,['G2a' id '/1'],['Sqrt' id '/1']);
    ln(mdl,['GKth' id '/1'],['Min' id '/1']); ln(mdl,['Sqrt' id '/1'],['Min' id '/2']);
    ln(mdl,['Min' id '/1'],['SatWn' id '/1']);
    ln(mdl,['SgnE' id '/1'],['PosOut' id '/1']); ln(mdl,['SatWn' id '/1'],['PosOut' id '/2']);
end

function [p, v] = traj(t, tgt, useTraj)
% quy dao di toi (0.1 -> 0.9 s) va ve (1.6 -> 2.4 s): da thuc bac 5 hoac bac thang
    p = zeros(size(t)); v = p;
    if ~useTraj
        p(t >= 0.1 & t < 1.6) = tgt;  return;
    end
    T = 0.8;
    for k = 1:numel(t)
        if t(k) < 1.6, [p(k), v(k)] = q5(t(k), 0.1, T, 0, tgt);
        else,          [p(k), v(k)] = q5(t(k), 1.6, T, tgt, 0); end
    end
end

function [p, v] = q5(t, t0, T, a, b)
    s = min(max((t - t0)/T, 0), 1);
    p = a + (b - a)*(10*s^3 - 15*s^4 + 6*s^5);
    v = (b - a)*(30*s^2 - 60*s^3 + 30*s^4)/T;
end

function plot_scope(ts, ttl)
    t = ts.Time;  d = squeeze(ts.Data);  if size(d,1) ~= numel(t), d = d.'; end
    lbl = {'goc (rad)','Speed wm (rad/s)','Armature current ia (A)'};
    col = {'r','b',[0.72 0.72 0]};
    figure('Name',ttl,'Color','w');
    for r = 1:3
        subplot(3,1,r); plot(t, d(:,r), 'Color', col{r}, 'LineWidth', 1.5); grid on; ylabel(lbl{r});
        if r == 1, title(ttl); end
    end
    xlabel('t (s)');
end

function plot_compare(tsList, names, ttl, row0)
    if nargin < 4, row0 = 2; end
    figure('Color','w','Name',ttl);
    rows = row0:3;  lbl = {'\theta (rad)','\omega (rad/s)','i_a (A)'};
    for r = 1:numel(rows)
        subplot(numel(rows),1,r); hold on; grid on;
        for k = 1:numel(tsList)
            d = squeeze(tsList{k}.Data); plot(tsList{k}.Time, d(:,rows(r)), 'LineWidth', 1.4);
        end
        ylabel(lbl{rows(r)}); legend(names);
        if r == 1, title(ttl); end
    end
    xlabel('t (s)');
end
