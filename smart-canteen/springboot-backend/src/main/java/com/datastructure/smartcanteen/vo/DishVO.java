package com.datastructure.smartcanteen.vo;

import lombok.Data;

import java.math.BigDecimal;
import java.time.LocalDateTime;

@Data
public class DishVO {

    private Long id;
    private Long categoryId;
    private String categoryName;
    private String name;
    private BigDecimal price;
    private String image;
    private String description;
    private Integer status;
    private LocalDateTime createTime;
}
