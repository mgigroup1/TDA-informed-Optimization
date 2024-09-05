function [YObj] = cost_total_D2sto_objcon_test(input)
% x: input

% input = [3.15, 26.7, 1120, 250, 0.01, 0.0025, 0.2, 0.2];
sample = [input(1), 26.7, 1120, 250, 0.01, 0.0025, input(2), 0.4];

if size(sample, 1) > size(sample, 2)
    sample = sample'
else
    sample
end

FR_API = sample(1);
FR_Exp = sample(2);

variable_mean=[3,250,2100,38,75,125,... %API
    26.7,400,2500,30,120,250,... %excipient
    0.3,200,1900,70,150,270,...  %lubricant
    1120,...
    250,...
    0.01,...
    0.0025];

variable_samp=[3,250,2100,38,75,125,... %API
    26.7,400,2500,30,120,250,... %excipient
    0.3,200,1900,70,150,270,...  %lubricant
    1120,...
    250,...
    0.01,...
    0.0025];

variable_samp(1) = sample(1);
variable_samp(7) = sample(2);
variable_samp(19) = sample(3);
variable_samp(20) = sample(4);
variable_samp(21) = sample(5);
variable_samp(22) = sample(6);

out_blender = blender(variable_samp);

tablet_outMean = tabletPress(variable_mean); % concentration; weight; hardness
concentrationMean = tablet_outMean(1);
weightMean = tablet_outMean(2);
hardnessMean = tablet_outMean(3);

% concentrationMean = param.concentrationMean;
% weightMean = param.concentrationMean;
% hardnessMean = param.concentrationMean;
bulkDensity = out_blender(5);



result_size = 4;
% x = [input(1),250,2100,38,75,125,... %API
%     input(2),400,2500,30,120,250,... %excipient
%     0.3,200,1900,70,150,270,...  %lubricant
%     input(3),...
%     input(4),...
%     input(5),...
%     input(6)];

gOMATLAB('startONLY');
gOMATLAB('select', 'Test_Rutgers_CDC_Module_April_edited_gOMATLAB5',...
    'Test_Rutgers_CDC_Module_April_edited_gOMATLAB5');
gOMATLAB('simulate', 'Test_Rutgers_CDC_Module_April_edited_gOMATLAB');

disp('evaluating the model:');
tic
for i = 1:1000
    result_matrix(i,:) = [i, gOMATLAB( 'evaluate', sample, result_size)];
    gstatus = result_matrix(i, 2 + result_size);
    if gstatus ~= 1
        disp('simulation failed.')
        result_matrix(i, :)
        break;
    end;
    
end
toc
gOMATLAB('stop');

% generate waste time-trajectory
waste_index = zeros(1000, 1); % unit is second
for i = 1:1000
    if ( result_matrix(i,3) > 1e-6 && (result_matrix(i,3) < 0.95*concentrationMean ||  result_matrix(i,3) > 1.05*concentrationMean) )...
        || ( result_matrix(i,4) > 1e-6 && (result_matrix(i,4) < 0.95*weightMean ||  result_matrix(i,4) > 1.05*weightMean) )...  
        || ( result_matrix(i,5) > 1e-6 && (result_matrix(i,5) < 0.95*hardnessMean ||  result_matrix(i,5) > 1.05*hardnessMean) )
        waste_index(i) = 1;
    end
end

% find the time interval between two qualified products
start_time = [];
end_time = [];

for i = 1:999
    if waste_index(i) < 1 && waste_index(i+1) >= 1
        start_time(end + 1) = i + 1;
    end
    if waste_index(i) >=1 && waste_index(i+1) < 1
        end_time(end + 1) = i;
    end
end


if isempty(end_time)
    total_waste_length = 24*3600 - start_time(1);
elseif length(end_time) == 1
    total_waste_length = end_time(1) - start_time(1);
else % length(end_time) is larger than 1
    total_waste_length = (min(end_time(1), 110) - start_time(1)) + ...
        ( sum(waste_index) - (min(end_time(1), 110) - start_time(1)) )...
        /(1000 - min(end_time(1), 110)) *(3600*24 - min(end_time(1), 110));
end


cost_waste = 15/3.78*(FR_API + FR_Exp + 0.3)/bulkDensity*1000 ... % $/h
                /3600*total_waste_length;
cost_utility = 1.5*(FR_API + FR_Exp + 0.3)*24;
cost_material = (109*FR_API + 139*FR_Exp + 74.4*0.3)*24;

cost_total = cost_waste + cost_utility + cost_material;

% f = cost_total;
disp(['waste: ', num2str(cost_waste), ', total: ', 'cost_total']);
%% noise-free output
YObj = cost_total;


end
