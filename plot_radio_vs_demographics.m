close all;
clear all;

handover_dists = readtable("./data/analysis/handover_dist_all.csv");
radio_kpis = readtable("./data/analysis/radio_kpis_all_interp.csv");
cell_dist = readtable("./data/analysis/cell_tower_distances.csv");

%{
plot_results(cell_dist, [0, 300, 1000, 3000, 5000, 10000], "cell_tower_distance", "population_density", "Distance to associated cell (km)", "Population density (people per sq mile)");
plot_results(handover_dists, [0, 300, 1000, 3000, 5000, 10000, 15000], "association_length", "population_density", "Distance between handovers (km)", "Population density (people per sq mile) ");
plot_results(radio_kpis, [0, 300, 1000, 3000, 5000, 10000, 15000], "num_seen_cells", "population_density", "Number of seen cells", "Population density (people per square mile)");
plot_results(radio_kpis, [0, 300, 1000, 3000, 5000, 10000, 15000], "rsrp", "population_density", "RSRP (dBm)", "Population density (people per square mile)");
plot_results(radio_kpis, [0, 300, 1000, 3000, 5000, 10000, 15000], "rsrq", "population_density", "RSRQ (dB)", "Population density (people per square mile)");
plot_results(radio_kpis, [0, 300, 1000, 3000, 5000, 10000, 15000], "rssi", "population_density", "RSSI (dBm)", "Population density (people per square mile)");

fenCodes = unique(radio_kpis.physiographic_region_fencode);
fenCodes = fenCodes(~cellfun('isempty', fenCodes));
% fenCodes = fenCodes(~isnan(fenCodes));
mean_rsrps = [];
mean_rsrqs =[];
num_samples = [];
mean_rssis = [];
rsrqs = [];
boxplot_label_group = {};

for idx = 1:numel(fenCodes)
    fenCode = char(fenCodes(idx));
    disp(fenCode);
    sel_table = radio_kpis(strcmp(radio_kpis.physiographic_region_fencode, fenCode), :);
    mean_rsrps = [mean_rsrps, mean(sel_table.rsrp)];
    mean_rsrqs =[mean_rsrqs, mean(sel_table.rsrq)];
    rsrqs = [rsrqs; sel_table.rsrq];
    b = boxplot(sel_table.rsrq, 'position', idx, 'Notch', 'on');
    hold on;
    mean_rssis = [mean_rssis, mean(sel_table.rssi)];
    num_samples = [num_samples, size(sel_table,1)];
    
end

figure
bar(fenCodes, mean_rsrps);
ylabel("Mean RSRP (dBm)");
xlabel("Physiogprahic province code");
grid on;

figure;
bar(fenCodes, mean_rsrqs);
ylabel("Mean RSRQ (dB)");
xlabel("Physiogprahic province code");
grid on;

figure;
bar(fenCodes, mean_rssis);
ylabel("Mean RSSI (dBm)");
xlabel("Physiogprahic province code");
grid on;

figure;
bar(fenCodes, num_samples);
ylabel("Number of data points")
xlabel("Physiographic region fencode")
grid on;

% RSRQ regions %%
RSRQ_Poor_Lower = -20;
RSRQ_Good_Upper = -10;

RSRP_Poor_Lower = -100
RSRP_Good_Upper = -80

% Classify into poor, acceptable, and good quality regions
demographics_range = [0, 300, 1000, 5000, 10000, 15000];
acceptable_ratios = [];
poor_ratios = [];
good_ratios = [];
for i = 1:(length(demographics_range)-1)
    sel_table = radio_kpis(radio_kpis.population_density > demographics_range(i) & radio_kpis.population_density < demographics_range(i + 1), :);
    poor_quality_indices = sel_table.rsrq <= RSRQ_Poor_Lower | sel_table.rsrp <= RSRP_Poor_Lower;
    good_quality_indices = sel_table.rsrq >= RSRQ_Good_Upper | sel_table.rsrp >= RSRQ_Good_Upper;
    acceptable_quality_regions = ~poor_quality_indices & ~good_quality_indices;
    acceptable_regions = sum(acceptable_quality_regions);
    good_regions = sum(good_quality_indices);
    poor_regions = sum(poor_quality_indices);
    total_regions = acceptable_regions + poor_regions + good_regions;

    good_ratios = [good_ratios, good_regions / total_regions];
    poor_ratios = [poor_ratios, poor_regions / total_regions];
    acceptable_ratios = [acceptable_ratios, acceptable_regions / total_regions];
end 

figure;
quality_analysis_summary = [poor_ratios; acceptable_ratios; good_ratios]';
bar(quality_analysis_summary);
legend({"< 300", "300-1000", ">1000"});


poor_quality_indices = (radio_kpis.rsrq <= RSRQ_Poor_Lower | radio_kpis.rsrp <= RSRP_Poor_Lower);
good_quality_indices = radio_kpis.rsrq >= RSRQ_Good_Upper | radio_kpis.rsrp >= RSRP_Good_Upper;
acceptable_quality_regions = ~poor_quality_indices & ~good_quality_indices;

% close all
figure
[fx, x] = ecdf(radio_kpis(poor_quality_indices, :).population_density);
hold on;
plot(x, fx, "DisplayName", "Poor quality");
[fx, x] = ecdf(radio_kpis(good_quality_indices, :).population_density);
hold on
plot(x,fx, "DisplayName", "Good quality")
[fx, x] = ecdf(radio_kpis(acceptable_quality_regions, :).population_density);
plot(x,fx, "DisplayName", "Acceptable quality")
legend show

% close all;

figure;

boxplot(radio_kpis(poor_quality_indices, :).population_density, 'Positions', 1);      
hold on;
boxplot(radio_kpis(acceptable_quality_regions, :).population_density, 'Positions', 2);     
hold on;
boxplot(radio_kpis(good_quality_indices, :).population_density, 'Positions', 3);          

ax = gca; % Get the current axes
ax.YAxis.Scale = 'log'; % Set the y-axis to logarithmic scale

%}
close all;
demographics_range = [0, 300];
for i = 1:(length(demographics_range)-1)
    sel_table = radio_kpis(radio_kpis.population_density > demographics_range(i) & radio_kpis.population_density < demographics_range(i + 1), :);
    sel_table.elevation(isnan(sel_table.elevation)) = 0;
    % calculate_terrain_ruggedness_index(sel_table());
    % elevations = sel_table.elevation(~isnan(sel_table.elevation));
    figure;
    scatter(sel_table.index, sel_table.elevation);
    xlabel(strcat("Data point index ", " pop density = ", num2str(demographics_range(i)), " to ", num2str(demographics_range(i+1)), " people per sq. mile"));
    ylabel("Elevation above ground (m)");
    disp("RSRP = ");
    mean(sel_table.rsrp)
    grid on;
end 

section_1 = [320580, 335484];

section_2 = [287025, 292405];
section_3 = [48457, 59807];
% figure;
% [f,xi] = ksdensity(radio_kpis(poor_quality_indices, :).population_density);
% plot(xi, f); hold on
% [f,xi] = ksdensity(radio_kpis(acceptable_quality_regions, :).population_density);
% plot(xi, f); hold on;
% [f,xi] = ksdensity(radio_kpis(good_quality_indices, :).population_density);
% plot(xi, f); hold on;




% boxplot(rsrqs, 'Notch', 'on', 'Labels',fenCodes);

% plot_results(radio_kpis, [0, 300, 1000, 3000, 5000, 10000, 15000], "cell_tower_distance", "population_density", "Cell tower distance (m)", "Population density (people per square mile)");


% plot_results(handover_dists, [0, 1.1, 2.1, 3.1, 4.1, 5.1, 6.1, 7.1, 8.1, 9.1], "association_length", "rucc");

% 

% mean_pop_density_ranges = [0, 300, 1000, 3000, 5000, 10000, 15000];
% 
% 
% for i = 1:(length(mean_pop_density_ranges)-1)
%     range_associated_lengths = table2array(handover_dists(handover_dists.population_density > mean_pop_density_ranges(i) & handover_dists.population_density < mean_pop_density_ranges(i + 1), "association_length"));
%     range_associated_lengths = range_associated_lengths(~isnan(range_associated_lengths) & range_associated_lengths ~= 0);
%     [cdf, dist] = ecdf(range_associated_lengths);
%     display_name = strcat(num2str(mean_pop_density_ranges(i)), " to ", num2str(mean_pop_density_ranges(i+1)));
% 
%     semilogx(dist, cdf, "DisplayName", display_name, LineWidth=3);
%     hold on;
% end
% 
% 
% 
% legend show;
% xlabel("Distance between handovers (km)");
% ylabel("CDF")
% grid on
% set(gca, "FontSize", 30);
% 
% mean_pop_tick_labels = [];
% 
% for i = 1:(length(mean_pop_density_ranges)-1)
%     mean_pop_tick_label = strcat(num2str(mean_pop_density_ranges(i)), " to ", num2str(mean_pop_density_ranges(i+1)));
%     mean_pop_tick_labels = [mean_pop_tick_labels, mean_pop_tick_label];
% end
% 
% mean_kpis = zeros(length(mean_pop_density_ranges) - 1, 1)
% for i = 1:(length(mean_pop_density_ranges) - 1)
%     kpis = table2array(handover_dists(handover_dists.population_density > mean_pop_density_ranges(i) & handover_dists.population_density < mean_pop_density_ranges(i + 1), "association_length"));
%     kpis = kpis(kpis ~=0);
%     mean_kpis(i) = mean(kpis)
% end
% 
% figure;
% bar(mean_kpis)
% xticklabels(mean_pop_tick_labels);
% xlabel("Population density (people per sq mile)");
% ylabel("Mean distance between handovers (km)");
% set(gca, "FontSize", 30);
% handover_dists.population_density

% 
% figure;
% scatter(handover_dists.population_density(handover_dists.association_length ~= 0), handover_dists.association_length(handover_dists.association_length ~= 0));
% xlabel("Population density (people per sq mile)");
% ylabel("Distance between handovers (km)");
% grid on;
% yticks(0:2.5:40)
% xticks(0:500:15000);
% set(gca, "FontSize", 28);