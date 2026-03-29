function [tri, distribution] = calculate_terrain_ruggedness_index(coordinates)
    coordinates.cum_distance = cumsum(coordinates.distance_to_next_point_meters);
   
    % coodinates.distance_to_mid_point = coodinates.cum_distance - mid_point;
    % Locate the central point
    % Calculate distance in meters between all points and the central point
    % 
   
end