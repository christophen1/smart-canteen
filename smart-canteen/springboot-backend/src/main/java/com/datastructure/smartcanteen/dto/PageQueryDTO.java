package com.datastructure.smartcanteen.dto;

import lombok.Data;

@Data
public class PageQueryDTO {

    private Integer page = 1;
    private Integer size = 10;
    private String keyword;
}
