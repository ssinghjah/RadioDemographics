dists = [0.1, 0.5, 1, 2];
markers = {'^', '*', 'x', 'o'};
close all;
fig = figure(1);
fig2 = figure(2);
fig3 = figure(3);
mean_rurals = zeros(size(dists));
mean_urbans = zeros(size(dists));
for dist_num = 1:numel(dists)
    dist = dists(dist_num);
    rural_pops = readtable(strcat("~/Work/AERPAW/ExperimentData/Cross_Country/AERPAW-1/Demographics/region_0_populations_handovers_per_dist_", num2str(dist) ,"_km.csv"));
    urban_pops = readtable(strcat("~/Work/AERPAW/ExperimentData/Cross_Country/AERPAW-1/Demographics/region_1_populations_handovers_per_dist_", num2str(dist) ,"_km.csv"));
    

    [cdf, rural_handovers_per_dist] = ecdf(rural_pops.num_handovers);
    figure(1), 
    plot(rural_handovers_per_dist, cdf,"--" , "Color", "#7E2F8E", Marker=char(markers(dist_num)), MarkerSize=16, LineWidth=2, DisplayName = strcat("rural ", num2str(dist), " km"));
    hold on;
    [cdf, urban_handovers_per_dist] = ecdf(urban_pops.num_handovers);
    plot(urban_handovers_per_dist, cdf, "Color", "#D95319", LineWidth=2, Marker=char(markers(dist_num)), MarkerSize=16, DisplayName = strcat("urban ", num2str(dist), " km"));
    
  
    edges = [0, 1, 2, 3, 4];
    centers = edges + 0.5;
    centers = centers(1:end-1);DisplayName = strcat(num2str(dist), " km")
    counts1 = histcounts(rural_pops.num_handovers, edges);
    counts2 = histcounts(urban_pops.num_handovers, edges);
    shift = 0.2
    figure;
    bar(centers - shift/2, counts1, 'BarWidth', 0.1, 'FaceColor', "#7E2F8E", 'FaceAlpha', 0.7);
    hold on;
    bar(centers + shift/2, counts2, 'BarWidth', 0.1, 'FaceColor', "#D95319", 'FaceAlpha', 0.7);
    title(strcat('Segment length = ', num2str(dist), " km"));


    mean_rurals(dist_num) = mean(rural_pops.num_handovers);
    mean_urbans(dist_num) = mean(urban_pops.num_handovers);


        
end

figure(1)
legend show;
xlabel("Number of handovers per segment");
ylabel("CDF");
xticks(0:1:15)
grid on;

figure(2);
scatter(dists, mean_rurals,'MarkerFaceColor', "#7E2F8E", DisplayName="Rural region");
hold on;
scatter(dists, mean_urbans, 'MarkerFaceColor', "#D95319", DisplayName="Urban region");
xlabel("Segment length (km)");
ylabel("Mean handovers per segment");
grid on;
legend  show;
