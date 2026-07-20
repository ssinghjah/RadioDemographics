close all;
clear all;

FONT_SIZE =30;

% --- Load data ---
% Nemo
nemo.handover_dists = readtable("./data/Nemo/analysis/handover_dist_all.csv");
nemo.radio_kpis     = readtable("./data/Nemo/analysis/radio_kpis_all.csv");
nemo.cell_dist      = readtable("./data/Nemo/analysis/cell_tower_distances.csv");
nemo.name           = "Nemo";

% PawPrints 2
pp2.handover_dists  = readtable("./data/PawPrints_2/analysis/handover_dist_all.csv");
pp2.radio_kpis      = readtable("./data/PawPrints_2/analysis/radio_kpis_all.csv");
pp2.cell_dist       = readtable("./data/PawPrints_2/analysis/cell_tower_distances.csv");
pp2.name            = "PawPrints 2";

% PawPrints 1
pp1.handover_dists  = readtable("./data/PawPrints_1/analysis/handover_dist_all.csv");
pp1.radio_kpis      = readtable("./data/PawPrints_1/analysis/radio_kpis_all.csv");
pp1.cell_dist       = readtable("./data/PawPrints_1/analysis/cell_tower_distances.csv");
pp1.name            = "PawPrints 1";

datasets.nemo = nemo;
datasets.pp1  = pp1;
datasets.pp2  = pp2;

plot_population_bin_counts(nemo, pp1, pp2);

% --- Compare devices  ---
ks_results = compute_ks_per_bin(datasets);
save_ks_results_csv(ks_results, "./ks_results_summary.csv");
plot_ks_heatmaps(ks_results);


% --- Run analysis ---
plot_radio_quality_analysis(nemo, FONT_SIZE);
plot_radio_quality_analysis(pp1, FONT_SIZE);
plot_radio_quality_analysis(pp2, FONT_SIZE);
plot_combined_quality_comparison({nemo, pp1, pp2}, FONT_SIZE);
plot_handover_analysis(pp1, FONT_SIZE);
plot_handover_analysis(pp2, FONT_SIZE);
plot_handover_analysis(nemo, FONT_SIZE);

function ks_results = compute_ks_per_bin(datasets)
    density_bins = [0, 300, 1000, 3000, 5000, 10000, 15000];
    n_bins = length(density_bins) - 1;

    names = fieldnames(datasets);
    n_datasets = length(names);

    % Store results
    ks_results = struct();

    for i = 1:n_datasets
        for j = i+1:n_datasets

            name1 = names{i};
            name2 = names{j};

            data1 = datasets.(name1).radio_kpis;
            data2 = datasets.(name2).radio_kpis;

            pair_name = sprintf('%s_vs_%s', name1, name2);

            ks_results.(pair_name).rsrp = zeros(n_bins, 2); % [ks_stat, p_value]
            ks_results.(pair_name).rsrq = zeros(n_bins, 2);

            for b = 1:n_bins

                % --- Select bin ---
                bin1 = data1( ...
                    data1.population_density > density_bins(b) & ...
                    data1.population_density <= density_bins(b+1), :);

                bin2 = data2( ...
                    data2.population_density > density_bins(b) & ...
                    data2.population_density <= density_bins(b+1), :);

                % --- Clean NaNs ---
                rsrp1 = bin1.rsrp(~isnan(bin1.rsrp));
                rsrp2 = bin2.rsrp(~isnan(bin2.rsrp));

                rsrq1 = bin1.rsrq(~isnan(bin1.rsrq));
                rsrq2 = bin2.rsrq(~isnan(bin2.rsrq));

                % --- KS test (only if both non-empty) ---
                if ~isempty(rsrp1) && ~isempty(rsrp2)
                    [~, p, ks] = kstest2(rsrp1, rsrp2);
                    ks_results.(pair_name).rsrp(b,:) = [ks, p];
                else
                    ks_results.(pair_name).rsrp(b,:) = [NaN, NaN];
                end

                if ~isempty(rsrq1) && ~isempty(rsrq2)
                    [~, p, ks] = kstest2(rsrq1, rsrq2);
                    ks_results.(pair_name).rsrq(b,:) = [ks, p];
                else
                    ks_results.(pair_name).rsrq(b,:) = [NaN, NaN];
                end

            end
        end
    end
end


% =========================================================================
function plot_population_bin_counts(nemo, pp1, pp2)

    density_bins = [0, 300, 1000, 3000, 5000, 10000, 15000];

    bin_labels = cell(1, length(density_bins)-1);
    for i = 1:length(density_bins)-1
        bin_labels{i} = sprintf("%d-%d", density_bins(i), density_bins(i+1));
    end

    devices = {nemo, pp1, pp2};
    device_names = ["Nemo", "PP1", "PP2"];

    count_matrix = zeros(length(devices), length(density_bins)-1);

    for d = 1:length(devices)

        data = devices{d}.radio_kpis;

        for b = 1:length(density_bins)-1

            sel = data( ...
                data.population_density > density_bins(b) & ...
                data.population_density <= density_bins(b+1), :);

            count_matrix(d, b) = size(sel, 1);

        end
    end

    % --- Plot heatmap ---
    figure;
    h = heatmap(bin_labels, device_names, count_matrix);

    h.Title = "Sample Count per Population Density Bin";
    h.XLabel = "Population Density Range";
    h.YLabel = "Device";

    colormap(parula);
end

function plot_radio_quality_analysis(dataset, FONT_SIZE)
    radio_kpis       = dataset.radio_kpis;
    dataset_name     = dataset.name;
    density_bins     = [0, 300, 1000, 3000, 5000, 10000, 15000];
    density_labels   = {'< 300','300-1000','1000-3000','3000-5000','5000-10000','10000-15000'};

    % --- Thresholds ---
    RSRQ_Poor_Lower  = -20;
    RSRQ_Good_Upper  = -10;
    RSRP_Poor_Lower  = -100;
    RSRP_Good_Upper  = -80;

    % --- RSRP box plot ---
    plot_results(radio_kpis, density_bins, "rsrp", "population_density", ...
        "RSRP (dBm)", "Population density (people per square mile)");
    title(sprintf("%s — RSRP vs Population Density", dataset_name));

    % --- RSRQ box plot ---
    plot_results(radio_kpis, density_bins, "rsrq", "population_density", ...
        "RSRQ (dB)", "Population density (people per square mile)");
    title(sprintf("%s — RSRQ vs Population Density", dataset_name));

    % --- Quality classification per density bin ---
    n_bins           = length(density_bins) - 1;
    poor_ratios      = zeros(1, n_bins);
    acceptable_ratios= zeros(1, n_bins);
    good_ratios      = zeros(1, n_bins);

    for i = 1:n_bins
        sel = radio_kpis( ...
            radio_kpis.population_density > density_bins(i) & ...
            radio_kpis.population_density < density_bins(i+1), :);

        is_poor       = sel.rsrq <= RSRQ_Poor_Lower | sel.rsrp <= RSRP_Poor_Lower;
        is_good       = sel.rsrq >= RSRQ_Good_Upper | sel.rsrp >= RSRP_Good_Upper;
        is_acceptable = ~is_poor & ~is_good;

        total              = size(sel, 1);
        poor_ratios(i)      = sum(is_poor)       / total;
        acceptable_ratios(i)= sum(is_acceptable) / total;
        good_ratios(i)      = sum(is_good)        / total;
    end

    figure;
    bar([poor_ratios; acceptable_ratios; good_ratios]');
    legend({"Poor quality", "Acceptable quality", "Good quality"});
    xlabel("Population density (people per sq. mile)");
    xticklabels(density_labels);
    ylabel("Fraction");
    grid on;

    % --- Quality classification over full dataset ---
    is_poor       = radio_kpis.rsrq <= RSRQ_Poor_Lower | radio_kpis.rsrp <= RSRP_Poor_Lower;
    is_good       = radio_kpis.rsrq >= RSRQ_Good_Upper | radio_kpis.rsrp >= RSRP_Good_Upper;
    is_acceptable = ~is_poor & ~is_good;

    % CDF of population density by quality class
    figure; hold on;
    [fx, x] = ecdf(radio_kpis(is_poor,       :).population_density);
    plot(x, fx, "DisplayName", "Poor quality");
    [fx, x] = ecdf(radio_kpis(is_good,        :).population_density);
    plot(x, fx, "DisplayName", "Good quality");
    [fx, x] = ecdf(radio_kpis(is_acceptable,  :).population_density);
    plot(x, fx, "DisplayName", "Acceptable quality");
    legend show;
    xlabel("Population density (people per sq. mile)");
    ylabel("CDF");
    grid on;

    % Boxplot of population density by quality class (log y-axis)
    figure; hold on;
    boxplot(radio_kpis(is_poor,       :).population_density, 'Positions', 1);
    boxplot(radio_kpis(is_acceptable, :).population_density, 'Positions', 2);
    boxplot(radio_kpis(is_good,       :).population_density, 'Positions', 3);
    ax = gca;
    ax.YAxis.Scale = 'log';
    xticklabels({'Poor', 'Acceptable', 'Good'});
    xlabel("Signal quality class");
    ylabel("Population density (log scale)");
    title(sprintf("%s — Population Density Boxplot by Quality Class", dataset_name));
    grid on;
    set(gca,"FontSize", FONT_SIZE)

end


function save_ks_results_csv(ks_results, filename)

    density_bins = [0, 300, 1000, 3000, 5000, 10000, 15000];
    n_bins = length(density_bins) - 1;

    pair_list = fieldnames(ks_results);

    rows = [];

    for b = 1:n_bins

        bin_label = sprintf("%d-%d", density_bins(b), density_bins(b+1));

        for kpi = ["RSRP", "RSRQ"]

            row = struct();
            row.population_id_range = bin_label;
            row.KPI = kpi;

            % Defaults
            row.nemo_vs_pp1_D = NaN; row.nemo_vs_pp1_p = NaN;
            row.nemo_vs_pp2_D = NaN; row.nemo_vs_pp2_p = NaN;
            row.pp1_vs_pp2_D  = NaN; row.pp1_vs_pp2_p  = NaN;

            for i = 1:length(pair_list)

                pair = pair_list{i};

                % Extract values
                if strcmp(kpi, "RSRP")
                    D = ks_results.(pair).rsrp(b,1);
                    p = ks_results.(pair).rsrp(b,2);
                elseif strcmp(kpi, "RSRQ")
                    D = ks_results.(pair).rsrq(b,1);
                    p = ks_results.(pair).rsrq(b,2);
                end

                % Map into correct columns
                if strcmp(pair, "nemo_vs_pp1")
                    row.nemo_vs_pp1_D = D;
                    row.nemo_vs_pp1_p = p;

                elseif strcmp(pair, "nemo_vs_pp2")
                    row.nemo_vs_pp2_D = D;
                    row.nemo_vs_pp2_p = p;

                elseif strcmp(pair, "pp1_vs_pp2")
                    row.pp1_vs_pp2_D = D;
                    row.pp1_vs_pp2_p = p;
                end

            end

            rows = [rows; row];

        end
    end

    % Convert to table
    T = struct2table(rows);

    % Write CSV
    writetable(T, filename);

    fprintf("KS results (D + p) saved to: %s\n", filename);
end


function plot_ks_heatmaps(ks_results)

    density_bins = [0, 300, 1000, 3000, 5000, 10000, 15000];
    bin_labels = cell(1, length(density_bins)-1);

    for i = 1:length(density_bins)-1
        bin_labels{i} = sprintf("%d-%d", density_bins(i), density_bins(i+1));
    end

    pairs = fieldnames(ks_results);

    metrics = ["rsrp", "rsrq"];
    metric_names = ["RSRP", "RSRQ"];

    for p = 1:length(pairs)

        pair = pairs{p};

        D_matrix = zeros(2, length(density_bins)-1);

        for m = 1:length(metrics)

            for b = 1:length(density_bins)-1
                D_matrix(m, b) = round(ks_results.(pair).(metrics(m))(b,1), 3);
            end

        end

        % --- Plot heatmap ---
        figure;
        h = heatmap(bin_labels, metric_names, D_matrix);

        h.Title = sprintf("KS Divergence (D) — %s", strrep(pair, "_", " "));
        h.XLabel = "Population density (people per sq. mile)";
        h.YLabel = "KPI (RSRP / RSRQ)";

        colormap(parula);
    end
end

function plot_combined_quality_comparison(devices, FONT_SIZE)

    density_bins = [0, 300, 1000, 3000, 5000, 10000, 15000];

    density_labels = { ...
        '0-300',...
        '300-1000',...
        '1000-3000',...
        '3000-5000',...
        '5000-10000',...
        '10000-15000'};

    RSRQ_Poor_Lower = -20;
    RSRQ_Good_Upper = -10;
    RSRP_Poor_Lower = -100;
    RSRP_Good_Upper = -80;

    nBins    = length(density_bins) - 1;
    nDevices = length(devices);

    poor_all       = zeros(nDevices, nBins);
    acceptable_all = zeros(nDevices, nBins);
    good_all       = zeros(nDevices, nBins);

    for d = 1:nDevices
        radio_kpis = devices{d}.radio_kpis;
        for i = 1:nBins
            sel = radio_kpis( ...
                radio_kpis.population_density > density_bins(i) & ...
                radio_kpis.population_density <= density_bins(i+1), :);
            total = height(sel);
            if total == 0
                poor_all(d,i)       = NaN;
                acceptable_all(d,i) = NaN;
                good_all(d,i)       = NaN;
                continue;
            end
            is_poor       = sel.rsrq <= RSRQ_Poor_Lower | sel.rsrp <= RSRP_Poor_Lower;
            is_good       = sel.rsrq >= RSRQ_Good_Upper | sel.rsrp >= RSRP_Good_Upper;
            is_acceptable = ~is_poor & ~is_good;
            poor_all(d,i)       = mean(is_poor);
            acceptable_all(d,i) = mean(is_acceptable);
            good_all(d,i)       = mean(is_good);
        end
    end

    names = string(cellfun(@(x) x.name, devices, 'UniformOutput', false));

    % Device colors from publication palette
    device_colors = [
        0.0000, 0.1882, 0.5020;   % Dark blue   — Nemo
        0.2902, 0.5647, 0.7686;   % Light blue  — PP1
        0.2902, 0.3765, 0.0627;   % Olive green — PP2
    ];

    x      = 1:nBins;
    markers = {'s', 'd', 'v'};

    %% ==========================================================
    %% Grouped bar — fraction per device, per bin
    %% ==========================================================

    quality_data   = {good_all,       acceptable_all,       poor_all};
    quality_titles = {"Good Quality",  "Acceptable Quality", "Poor Quality"};
    quality_ylabels= {"Fraction Good", "Fraction Acceptable","Fraction Poor"};

    for q = 1:3

        figure;
        b = bar(quality_data{q}');   % nBins x nDevices matrix → grouped bars
        
        for d = 1:nDevices
            b(d).FaceColor = device_colors(d,:);
            b(d).DisplayName = names(d);
        end

        xticks(1:nBins);
        xticklabels(density_labels);
        xlabel('Population density (people per sq. mile)');
        ylabel(quality_ylabels{q});
        title(quality_titles{q});
        legend('Location', 'best');
        grid on;
        set(gca, 'FontSize', FONT_SIZE);

    end

    %% ==========================================================
    %% GOOD QUALITY — line plot
    %% ==========================================================

    figure; hold on;
    for d = 1:nDevices
        plot(x, good_all(d,:), ...
            '-', 'LineWidth', 3, ...
            'Marker', markers{d}, ...
            'MarkerSize', 15, ...
            'Color', device_colors(d,:), ...
            'DisplayName', names(d));
    end
    xticks(x); xticklabels(density_labels);
    xlabel('Population density (people per sq. mile)');
    ylabel('Fraction Good Quality');
    title('Good Signal Quality Comparison');
    legend('Location', 'best');
    grid on;
    set(gca, 'FontSize', FONT_SIZE);

    %% ==========================================================
    %% ACCEPTABLE QUALITY — line plot
    %% ==========================================================

    figure; hold on;
    for d = 1:nDevices
        plot(x, acceptable_all(d,:), ...
            '-', 'LineWidth', 3, ...
            'Marker', markers{d}, ...
            'MarkerSize', 15, ...
            'Color', device_colors(d,:), ...
            'DisplayName', names(d));
    end
    xticks(x); xticklabels(density_labels);
    xlabel('Population density (people per sq. mile)');
    ylabel('Fraction Acceptable Quality');
    title('Acceptable Signal Quality Comparison');
    legend('Location', 'best');
    grid on;
    set(gca, 'FontSize', FONT_SIZE);

    %% ==========================================================
    %% POOR QUALITY — line plot
    %% ==========================================================

    figure; hold on;
    for d = 1:nDevices
        plot(x, poor_all(d,:), ...
            '-', 'LineWidth', 3, ...
            'Marker', markers{d}, ...
            'MarkerSize', 15, ...
            'Color', device_colors(d,:), ...
            'DisplayName', names(d));
    end
    xticks(x); xticklabels(density_labels);
    xlabel('Population density (people per sq. mile)');
    ylabel('Fraction Poor Quality');
    title('Poor Signal Quality Comparison');
    legend('Location', 'best');
    grid on;
    set(gca, 'FontSize', FONT_SIZE);

    %% ==========================================================
    %% SCATTER VERSION
    %% ==========================================================

    figure; hold on;
    markers_scatter = {'s', '^', 'v'};
    good_color       = [0.0,  0.6,  0.0];
    acceptable_color = [1.0,  0.55, 0.0];
    poor_color       = [0.85, 0.0,  0.0];

    for d = 1:nDevices
        scatter(x, good_all(d,:),       500, good_color,       markers_scatter{d}, 'filled', 'DisplayName', sprintf('%s Good',       names(d)));
        scatter(x, acceptable_all(d,:), 500, acceptable_color, markers_scatter{d}, 'filled', 'DisplayName', sprintf('%s Acceptable', names(d)));
        scatter(x, poor_all(d,:),       500, poor_color,       markers_scatter{d}, 'filled', 'DisplayName', sprintf('%s Poor',       names(d)));
    end

    xticks(x); xticklabels(density_labels);
    xlabel('Population density (people per sq. mile)');
    ylabel('Fraction');
    title('Signal Quality Scatter Comparison');
    legend('Location', 'eastoutside');
    grid on;
    set(gca, 'FontSize', FONT_SIZE);

    %% ==========================================================
    %% ALL DEVICES + ALL QUALITY LEVELS — line plot
    %% ==========================================================

    figure; hold on;
    line_styles = {'-', '--', ':'};
    markers_all = {'o', 's', 'd'};

    for d = 1:nDevices
        plot(x, good_all(d,:),       'Color', good_color,       'LineStyle', line_styles{d}, 'Marker', markers_all{d}, 'LineWidth', 3, 'MarkerSize', 10, 'DisplayName', sprintf('%s Good',       names(d)));
        plot(x, acceptable_all(d,:), 'Color', acceptable_color, 'LineStyle', line_styles{d}, 'Marker', markers_all{d}, 'LineWidth', 3, 'MarkerSize', 10, 'DisplayName', sprintf('%s Acceptable', names(d)));
        plot(x, poor_all(d,:),       'Color', poor_color,       'LineStyle', line_styles{d}, 'Marker', markers_all{d}, 'LineWidth', 3, 'MarkerSize', 10, 'DisplayName', sprintf('%s Poor',       names(d)));
    end

    xticks(x); xticklabels(density_labels);
    xlabel('Population density (people per sq. mile)');
    ylabel('Fraction of Samples');
    title('Signal Quality Comparison by Device and Population Density');
    legend('Location', 'eastoutside');
    grid on;
    set(gca, 'FontSize', FONT_SIZE);

end


function plot_handover_analysis(dataset, FONT_SIZE)

    handover_dists = dataset.handover_dists;
    dataset_name   = dataset.name;

    density_bins = [0, 300, 1000, 3000, 5000, 10000, 15000];

    density_labels = { ...
        '0-300',...
        '300-1000',...
        '1000-3000',...
        '3000-5000',...
        '5000-10000',...
        '10000-15000'};

    % Population density colors
       colors = [
        0.0000, 0.1882, 0.5020;   % Dark blue
        0.2902, 0.5647, 0.7686;   % Light blue
        0.2902, 0.3765, 0.0627;   % Olive green
        0.8314, 0.6588, 0.0000;   % Mustard
        0.8784, 0.4392, 0.1255;   % Orange
        0.8000, 0.0667, 0.0667;   % Red
    ];
    
    line_styles = {
        ':', ...
        ':o', ...
        '--s', ...
        '--*', ...
        '--', ...
        '-'
    };

    %% ==========================================================
    %% Handover Distance CDF
    %% ==========================================================

    figure;
    hold on;

    for i = 1:length(density_bins)-1

        vals = handover_dists.association_length( ...
            handover_dists.population_density > density_bins(i) & ...
            handover_dists.population_density <= density_bins(i+1));

        vals = vals(~isnan(vals) & vals > 0);

        if isempty(vals)
            continue;
        end

        [cdf, dist] = ecdf(vals);

        label = sprintf('%d-%d ppsm', ...
            density_bins(i), density_bins(i+1));

        semilogx(dist, cdf, ...
            'Color', colors(i,:), ...
            'LineWidth', 3, ...
            'DisplayName', label);
    end

    xlabel('Distance between handovers (km)');
    ylabel('CDF');
    title(sprintf('%s - Handover Distance CDF', dataset_name));
    legend('Location','best');
    grid on;
    set(gca,'FontSize',FONT_SIZE);

    %% ==========================================================
    %% Mean Handover Distance
    %% ==========================================================

    mean_dist = nan(length(density_bins)-1,1);
    std_dist  = nan(length(density_bins)-1,1);
    
    for i = 1:length(density_bins)-1
    
        vals = handover_dists.association_length( ...
            handover_dists.population_density > density_bins(i) & ...
            handover_dists.population_density <= density_bins(i+1));
    
        vals = vals(~isnan(vals) & vals > 0);
    
        if ~isempty(vals)
            mean_dist(i) = mean(vals);
            std_dist(i)  = std(vals);
        end
    end

    figure;

    b = bar(mean_dist);

    hold on;

    errorbar( ...
        1:length(mean_dist), ...
        mean_dist, ...
        std_dist, ...
        'k.', ...
        'LineWidth',2, ...
        'CapSize',12);

    b.FaceColor = 'flat';
    b.CData = colors;

    xticks(1:length(density_labels));
    xticklabels(density_labels);

    xlabel('Population density (people per sq. mile)');
    ylabel('Mean Distance between handovers (km)');
    title(sprintf('%s - Mean Handover Distance', dataset_name));

    grid on;
    set(gca,'FontSize',FONT_SIZE);

    %% ==========================================================
    %% Handover Distance Box Plot
    %% ==========================================================

    figure;

    box_data  = [];
    box_group = [];

    for i = 1:length(density_bins)-1

        vals = handover_dists.association_length( ...
            handover_dists.population_density > density_bins(i) & ...
            handover_dists.population_density <= density_bins(i+1));

        vals = vals(~isnan(vals) & vals > 0);

        box_data  = [box_data; vals];
        box_group = [box_group; repmat(i,length(vals),1)];
    end

    boxplot(box_data, box_group, ...
        'Colors','k', ...
        'Symbol','.', ...
        'Widths',0.6);

    hold on;

    h = findobj(gca,'Tag','Box');

    for k = 1:length(h)
        idx = length(h)-k+1;    % MATLAB returns boxes in reverse order

        patch( ...
            get(h(k),'XData'), ...
            get(h(k),'YData'), ...
            colors(idx,:), ...
            'FaceAlpha',0.5, ...
            'EdgeColor',colors(idx,:), ...
            'LineWidth',2);
    end

    % Bring box outlines/median back to the front
    med = findobj(gca,'Tag','Median');
    set(med, ...
        'LineWidth', 4, ...      % increase median thickness
        'Color', 'k');           % black median line
    
    % Bring box outlines/median back to the front
    uistack(med,'top');
    uistack(findobj(gca,'Tag','Whisker'),'top');
    uistack(findobj(gca,'Tag','Upper Whisker'),'top');
    uistack(findobj(gca,'Tag','Lower Whisker'),'top');

    xticks(1:length(density_labels));
    xticklabels(density_labels);

    xlabel('Population density (people per sq. mile)');
    ylabel('Distance between handovers (km)');
    title(sprintf('%s - Handover Distance Distribution', dataset_name));

    grid on;
    set(gca,'FontSize',FONT_SIZE);


end

%{


close all;
clear all;

% --- Load data ---
% Nemo
nemo.handover_dists = readtable("./data/Nemo/analysis/handover_dist_all.csv");
nemo.radio_kpis     = readtable("./data/Nemo/analysis/radio_kpis_all.csv");
nemo.cell_dist      = readtable("./data/Nemo/analysis/cell_tower_distances.csv");
nemo.name           = "Nemo";

% PawPrints 2
pp2.handover_dists  = readtable("./data/PawPrints2/analysis/handover_dist_all.csv");
pp2.radio_kpis      = readtable("./data/PawPrints2/analysis/radio_kpis_all.csv");
pp2.cell_dist       = readtable("./data/PawPrints2/analysis/cell_tower_distances.csv");
pp2.name            = "PawPrints 2";

% PawPrints 1
pp1.handover_dists  = readtable("./data/PawPrints1/analysis/handover_dist_all.csv");
pp1.radio_kpis      = readtable("./data/PawPrints1/analysis/radio_kpis_all.csv");
pp1.cell_dist       = readtable("./data/PawPrints1/analysis/cell_tower_distances.csv");
pp1.name            = "PawPrints 1";

% --- Run analysis ---
plot_radio_quality_analysis(nemo);
% plot_radio_quality_analysis(pp2);
% plot_radio_quality_analysis(pp1);


% =========================================================================
function plot_radio_quality_analysis(dataset)
% PLOT_RADIO_QUALITY_ANALYSIS  Plots RSRP, RSRQ, and signal quality
%   breakdown for a given dataset struct.
%
%   dataset fields:
%     .radio_kpis  - table with columns: rsrp, rsrq, population_density
%     .name        - string label used in figure titles (e.g. "Nemo")

    radio_kpis       = dataset.radio_kpis;
    dataset_name     = dataset.name;
    density_bins     = [0, 300, 1000, 3000, 5000, 10000, 15000];
    density_labels   = {'< 300','300-1000','1000-3000','3000-5000','5000-10000','10000-15000'};

    % --- Thresholds ---
    RSRQ_Poor_Lower  = -20;
    RSRQ_Good_Upper  = -10;
    RSRP_Poor_Lower  = -100;
    RSRP_Good_Upper  = -80;

    % --- RSRP box plot ---
    plot_results(radio_kpis, density_bins, "rsrp", "population_density", ...
        "RSRP (dBm)", "Population density (people per square mile)");
    title(sprintf("%s — RSRP vs Population Density", dataset_name));

    % --- RSRQ box plot ---
    plot_results(radio_kpis, density_bins, "rsrq", "population_density", ...
        "RSRQ (dB)", "Population density (people per square mile)");
    title(sprintf("%s — RSRQ vs Population Density", dataset_name));

    % --- Quality classification per density bin ---
    n_bins           = length(density_bins) - 1;
    poor_ratios      = zeros(1, n_bins);
    acceptable_ratios= zeros(1, n_bins);
    good_ratios      = zeros(1, n_bins);

    for i = 1:n_bins
        sel = radio_kpis( ...
            radio_kpis.population_density > density_bins(i) & ...
            radio_kpis.population_density < density_bins(i+1), :);

        is_poor       = sel.rsrq <= RSRQ_Poor_Lower | sel.rsrp <= RSRP_Poor_Lower;
        is_good       = sel.rsrq >= RSRQ_Good_Upper | sel.rsrp >= RSRP_Good_Upper;
        is_acceptable = ~is_poor & ~is_good;

        total              = size(sel, 1);
        poor_ratios(i)      = sum(is_poor)       / total;
        acceptable_ratios(i)= sum(is_acceptable) / total;
        good_ratios(i)      = sum(is_good)        / total;
    end

    figure;
    bar([poor_ratios; acceptable_ratios; good_ratios]');
    legend({"Poor quality", "Acceptable quality", "Good quality"});
    xlabel("Population density (people per sq. mile)");
    xticklabels(density_labels);
    ylabel("Fraction");
    title(sprintf("%s — Signal Quality by Population Density", dataset_name));
    grid on;

    % --- Quality classification over full dataset ---
    is_poor       = radio_kpis.rsrq <= RSRQ_Poor_Lower | radio_kpis.rsrp <= RSRP_Poor_Lower;
    is_good       = radio_kpis.rsrq >= RSRQ_Good_Upper | radio_kpis.rsrp >= RSRP_Good_Upper;
    is_acceptable = ~is_poor & ~is_good;

    % CDF of population density by quality class
    figure; hold on;
    [fx, x] = ecdf(radio_kpis(is_poor,       :).population_density);
    plot(x, fx, "DisplayName", "Poor quality");
    [fx, x] = ecdf(radio_kpis(is_good,        :).population_density);
    plot(x, fx, "DisplayName", "Good quality");
    [fx, x] = ecdf(radio_kpis(is_acceptable,  :).population_density);
    plot(x, fx, "DisplayName", "Acceptable quality");
    legend show;
    xlabel("Population density");
    ylabel("CDF");
    title(sprintf("%s — Population Density CDF by Quality Class", dataset_name));
    grid on;

    % Boxplot of population density by quality class (log y-axis)
    figure; hold on;
    boxplot(radio_kpis(is_poor,       :).population_density, 'Positions', 1);
    boxplot(radio_kpis(is_acceptable, :).population_density, 'Positions', 2);
    boxplot(radio_kpis(is_good,       :).population_density, 'Positions', 3);
    ax = gca;
    ax.YAxis.Scale = 'log';
    xticklabels({'Poor', 'Acceptable', 'Good'});
    xlabel("Signal quality class");
    ylabel("Population density (log scale)");
    title(sprintf("%s — Population Density Boxplot by Quality Class", dataset_name));
    grid on;

end


% Nemo
handover_dists = readtable("./data/Nemo/analysis/handover_dist_all.csv");
radio_kpis = readtable("./data/Nemo/analysis/radio_kpis_all.csv");
cell_dist = readtable("./data/Nemo/analysis/cell_tower_distances.csv");



% plot_results(cell_dist, [0, 300, 1000, 3000, 5000, 10000], "cell_tower_distance", "population_density", "Distance to associated cell (km)", "Population density (people per sq mile)");
% plot_results(handover_dists, [0, 300, 1000, 3000, 5000, 10000, 15000], "association_length", "population_density", "Distance between handovers (km)", "Population density (people per sq mile) ");
% plot_results(radio_kpis, [0, 300, 1000, 3000, 5000, 10000, 15000], "num_seen_cells", "population_density", "Number of seen cells", "Population density (people per square mile)");
plot_results(radio_kpis, [0, 300, 1000, 3000, 5000, 10000, 15000], "rsrp", "population_density", "RSRP (dBm)", "Population density (people per square mile)");
plot_results(radio_kpis, [0, 300, 1000, 3000, 5000, 10000, 15000], "rsrq", "population_density", "RSRQ (dB)", "Population density (people per square mile)");
% plot_results(radio_kpis, [0, 300, 1000, 3000, 5000, 10000, 15000], "rssi", "population_density", "RSSI (dBm)", "Population density (people per square mile)");

% fenCodes = unique(radio_kpis.physiographic_region_fencode);
% fenCodes = fenCodes(~cellfun('isempty', fenCodes));
% % fenCodes = fenCodes(~isnan(fenCodes));
% mean_rsrps = [];
% mean_rsrqs =[];
% num_samples = [];
% mean_rssis = [];
% rsrqs = [];
% boxplot_label_group = {};
% 
% for idx = 1:numel(fenCodes)
%     fenCode = char(fenCodes(idx));
%     disp(fenCode);
%     sel_table = radio_kpis(strcmp(radio_kpis.physiographic_region_fencode, fenCode), :);
%     mean_rsrps = [mean_rsrps, mean(sel_table.rsrp)];
%     mean_rsrqs =[mean_rsrqs, mean(sel_table.rsrq)];
%     rsrqs = [rsrqs; sel_table.rsrq];
%     b = boxplot(sel_table.rsrq, 'position', idx, 'Notch', 'on');
%     hold on;
%     mean_rssis = [mean_rssis, mean(sel_table.rssi)];
%     num_samples = [num_samples, size(sel_table,1)];
% 
% end
% 
% figure
% bar(fenCodes, mean_rsrps);
% ylabel("Mean RSRP (dBm)");
% xlabel("Physiogprahic province code");
% grid on;
% 
% figure;
% bar(fenCodes, mean_rsrqs);
% ylabel("Mean RSRQ (dB)");
% xlabel("Physiogprahic province code");
% grid on;
% 
% figure;
% bar(fenCodes, mean_rssis);
% ylabel("Mean RSSI (dBm)");
% xlabel("Physiogprahic province code");
% grid on;
% 
% figure;
% bar(fenCodes, num_samples);
% ylabel("Number of data points")
% xlabel("Physiographic region fencode")
% grid on;

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
legend({"Poor quality", "Acceptable quality", "Good quality"});
xlabel("Population density (people per sq. mile)")
xticklabels({'< 300', '300-1000', '1000-5000', '5000-10000', '10000-15000'})
ylabel("Fraction")


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
xlabel("Population density")
ylabel("CDF")

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
% close all;
% demographics_range = [0, 300];
% for i = 1:(length(demographics_range)-1)
%     sel_table = radio_kpis(radio_kpis.population_density > demographics_range(i) & radio_kpis.population_density < demographics_range(i + 1), :);
%     sel_table.elevation(isnan(sel_table.elevation)) = 0;
%     % calculate_terrain_ruggedness_index(sel_table());
%     % elevations = sel_table.elevation(~isnan(sel_table.elevation));
%     figure;
%     scatter(sel_table.index, sel_table.elevation);
%     xlabel(strcat("Data point index ", " pop density = ", num2str(demographics_range(i)), " to ", num2str(demographics_range(i+1)), " people per sq. mile"));
%     ylabel("Elevation above ground (m)");
%     disp("RSRP = ");
%     mean(sel_table.rsrp)
%     grid on;
% end 

% section_1 = [320580, 335484];
% 
% section_2 = [287025, 292405];
% section_3 = [48457, 59807];
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

%}