function y = plot_results(radio_demographics, demographics_range, radio_kpi, demographics_kpi, radio_kpi_label, demographics_kpi_label)

    figure;
    if demographics_kpi == "population_density"
        demographics = radio_demographics.population_density;
    elseif demographics_kpi == "rucc"
            demographics = radio_demographics.rucc;
    end

    for i = 1:(length(demographics_range)-1)
        range_associated_lengths = table2array(radio_demographics(demographics > demographics_range(i) & demographics < demographics_range(i + 1), radio_kpi));
        range_associated_lengths = range_associated_lengths(~isnan(range_associated_lengths) & range_associated_lengths ~= 0);
        [cdf, dist] = ecdf(range_associated_lengths);
        display_name = strcat(num2str(demographics_range(i)), " to ", num2str(demographics_range(i+1)));
        semilogx(dist, cdf, "DisplayName", display_name, LineWidth=3);
        hold on;        
    end 
    y = 1;
        legend show;
        xlabel(radio_kpi_label);
        ylabel(strcat("CDF of ", radio_kpi_label));
        grid on
        set(gca, "FontSize", 30);

    mean_pop_tick_labels = [];

    for i = 1:(length(demographics_range)-1)
        mean_pop_tick_label = strcat(num2str(demographics_range(i)), " to ", num2str(demographics_range(i+1)));
        mean_pop_tick_labels = [mean_pop_tick_labels, mean_pop_tick_label];
    end
    
    mean_kpis = zeros(length(demographics_range) - 1, 1)
    for i = 1:(length(demographics_range) - 1)
        kpis = table2array(radio_demographics(demographics> demographics_range(i) & demographics < demographics_range(i + 1), radio_kpi));
        kpis = kpis(kpis ~=0);
        mean_kpis(i) = mean(kpis);
    end
    
    figure;
    bar(mean_kpis)
    xticklabels(mean_pop_tick_labels);
    xlabel(demographics_kpi_label);
    ylabel(radio_kpi_label);
    set(gca, "FontSize", 30);


    figure;
    valid_radio_kpi_rows = radio_demographics.(radio_kpi) ~= 0;
    scatter(table2array(radio_demographics(valid_radio_kpi_rows, demographics_kpi)), table2array(radio_demographics(valid_radio_kpi_rows, radio_kpi)));
    xlabel(demographics_kpi_label);
    ylabel(radio_kpi_label);
    grid on;
    % yticks(0:2.5:40);
    xticks(0:1000:25000);
    set(gca, "FontSize", 28);


end