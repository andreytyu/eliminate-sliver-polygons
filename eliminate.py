def eliminate_sliver_polygons(df_to_elim, poly, field, threshold):
    '''
        Eliminates sliver polygons based on the field value:

        df_to_elim (GeoDataFrame): DataFrame to clear of slivers;
        poly (Shapely Polygon): bounding city polygon;
        field (str): value columnn;
        threshold (int): value below which polygons are considered slevers
    '''
    df_good, df_bad = [x for _, x in df_to_elim.groupby(
        df_to_elim[field] < threshold)]
    do_i_loop = True
    num_slivers = len(df_bad)

    while do_i_loop:
        df_good = df_good.reset_index(drop=True)
        df_bad = df_bad.reset_index(drop=True)

        for x in tqdm(range(len(df_bad))):

            dists = [df_bad.geometry[x].distance(
                poly) for poly in df_good['geometry']]
            df_good['current_distance'] = dists

            df_close = df_good[df_good.current_distance == 0].reset_index(drop=True)

            if len(df_close) == 0:
                continue
                
            else:
                len_dict = {}
                for y in range(len(df_close)):
                    len_dict[df_close['id'][y]] = df_bad.geometry[x].boundary.intersection(
                        df_close.geometry[y].boundary).length
                if max(len_dict.values()) == 0:
                    continue
                maxValKey = max(len_dict, key=len_dict.get)
                df_good.loc[
                    df_good.id == maxValKey, ['geometry']] = df_close.loc[
                    df_close['id'] == maxValKey]['geometry'].tolist()[0].union(df_bad.geometry[x])

                df_bad = df_bad.drop(x, axis=0)

        new_num_slivers = len(df_bad)

        if num_slivers - new_num_slivers == 0:
            do_i_loop = False
        else:
            do_i_loop = True

        num_slivers = new_num_slivers
    return(df_good)