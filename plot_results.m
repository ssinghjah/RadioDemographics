function y = plot_results(radio_demographics, demographics_range, ...
    radio_kpi, demographics_kpi, radio_kpi_label, demographics_kpi_label)

    figure;

    % =========================
    % Demographics selection
    % =========================
    if demographics_kpi == "population_density"
        demographics = radio_demographics.population_density;
    elseif demographics_kpi == "rucc"
        demographics = radio_demographics.rucc;
    end

    % =========================
    % SAME COLOR PALETTE AS MAIN SCRIPT
    % =========================
    colors = [
        0.0000, 0.1882, 0.5020;   % Dark blue
        0.2902, 0.5647, 0.7686;   % Light blue
        0.2902, 0.3765, 0.0627;   % Olive green
        0.8314, 0.6588, 0.0000;   % Mustard
        0.8784, 0.4392, 0.1255;   % Orange
        0.8000, 0.0667, 0.0667;   % Red
    ];

    line_styles = {
        ':', ':o', '--s', '--*', '--', '-'
    };

    nBins = length(demographics_range) - 1;

    %% =========================
    % CDF PLOT
    %% =========================
    for i = 1:nBins

        vals = table2array(radio_demographics( ...
            demographics > demographics_range(i) & ...
            demographics < demographics_range(i+1), ...
            radio_kpi));

        vals = vals(~isnan(vals) & vals ~= 0);

        [cdf, dist] = ecdf(vals);

        label = strcat(num2str(demographics_range(i)), " to ", ...
                       num2str(demographics_range(i+1)));

        semilogx(dist, cdf, ...
            line_styles{i}, ...
            "DisplayName", label, ...
            "LineWidth", 3, ...
            "Color", colors(i,:), ...
            "MarkerSize", 18);

        hold on;
    end

    legend show;
    xlabel(radio_kpi_label);
    ylabel("CDF of " + radio_kpi_label);
    grid on;
    set(gca, "FontSize", 30);

    %% =========================
    % MEAN BAR PLOT
    %% =========================
    mean_labels = strings(1, nBins);
    mean_vals = zeros(nBins, 1);

    for i = 1:nBins

        mean_labels(i) = strcat(num2str(demographics_range(i)), ...
                                " to ", ...
                                num2str(demographics_range(i+1)));

        vals = table2array(radio_demographics( ...
            demographics > demographics_range(i) & ...
            demographics < demographics_range(i+1), ...
            radio_kpi));

        vals = vals(vals ~= 0 & ~isnan(vals));
        mean_vals(i) = mean(vals);
    end

    figure;
    b = bar(mean_vals);
    b.FaceColor = 'flat';
    b.CData = colors(1:nBins,:);

    xticklabels(mean_labels);
    xlabel(demographics_kpi_label);
    ylabel(radio_kpi_label);
    grid on;
    set(gca, "FontSize", 30);

    %% =========================
    % SCATTER PLOT
    %% =========================
    figure;
    valid = radio_demographics.(radio_kpi) ~= 0;

    scatter( ...
        table2array(radio_demographics(valid, demographics_kpi)), ...
        table2array(radio_demographics(valid, radio_kpi)));

    xlabel(demographics_kpi_label);
    ylabel(radio_kpi_label);
    grid on;
    set(gca, "FontSize", 28);

    %% =========================
    % BOX PLOT (FIXED COLORING)
    %% =========================
    figure; hold on;

    box_data = [];
    box_group = [];

    for i = 1:nBins

        vals = table2array(radio_demographics( ...
            demographics > demographics_range(i) & ...
            demographics < demographics_range(i+1), ...
            radio_kpi));

        vals = vals(~isnan(vals) & vals ~= 0);

        box_data = [box_data; vals];
        box_group = [box_group; repmat(i, length(vals), 1)];
    end

    boxplot(box_data, box_group, ...
        'Colors', 'k', ...
        'Symbol', '.');

    % ---- COLOR EACH BOX USING SAME PALETTE ----
    h = findobj(gca, 'Tag', 'Box');

    for k = 1:length(h)
        idx = length(h) - k + 1;   % correct order
        patch(get(h(k), 'XData'), ...
              get(h(k), 'YData'), ...
              colors(idx, :), ...
              'FaceAlpha', 0.5, ...
              'EdgeColor', colors(idx,:), ...
              'LineWidth', 2);
    end

    xticks(1:nBins);
    xticklabels(mean_labels);

    xlabel(demographics_kpi_label);
    ylabel(radio_kpi_label);
    title("Boxplot of " + radio_kpi_label + " by " + demographics_kpi_label);

    grid on;
    set(gca, "FontSize", 30);

end